from collections import defaultdict
from collections.abc import Set as AbstractSet
from typing import Annotated, Any
from warnings import warn

from atoti_core import (
    DEPRECATED_WARNING_CATEGORY as _DEPRECATED_WARNING_CATEGORY,
    PYDANTIC_CONFIG as _PYDANTIC_CONFIG,
    HierarchyIdentifier,
    Identifiable,
    LevelIdentifier,
    identify,
)
from pydantic import AfterValidator, Field, model_validator
from pydantic.dataclasses import dataclass
from typing_extensions import override

from .._measure_convertible import NonConstantMeasureConvertible
from .._measure_description import MeasureDescription
from .._measures.calculated_measure import AggregatedMeasure
from ._base_scope import BaseScope


def _check_unique_hierarchies(
    levels: AbstractSet[Identifiable[LevelIdentifier]], /
) -> AbstractSet[Identifiable[LevelIdentifier]]:
    levels_grouped_by_hierarchy: dict[HierarchyIdentifier, set[str]] = defaultdict(set)

    for level in levels:
        level_identifier = identify(level)
        levels_grouped_by_hierarchy[level_identifier.hierarchy_identifier].add(
            level_identifier.level_name
        )

    duplicate_hierarchies = {
        hierarchy_identifier
        for hierarchy_identifier, level_names in levels_grouped_by_hierarchy.items()
        if len(level_names) > 1
    }
    if duplicate_hierarchies:
        raise ValueError(
            f"The passed levels must belong to different hierarchies but several levels were given for {duplicate_hierarchies}."
        )

    return levels


@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class OriginScope(BaseScope):  # pylint: disable=keyword-only-dataclass, make it keyword only when dropping the deprecated constructor.
    """Scope performing an aggregation at the given origin.

    The input of the aggregation function will be evaluated at the given :attr:`levels` and the aggregation function will be applied "above" these intermediate aggregates.

    Example:
        Using this scope with :func:`atoti.agg.mean` to average quantities summed by month:

        >>> df = pd.DataFrame(
        ...     columns=["Year", "Month", "Day", "Quantity"],
        ...     data=[
        ...         (2019, 7, 1, 15),
        ...         (2019, 7, 2, 20),
        ...         (2019, 7, 3, 30),
        ...         (2019, 6, 1, 25),
        ...         (2019, 6, 2, 15),
        ...         (2018, 7, 1, 5),
        ...         (2018, 7, 2, 10),
        ...         (2018, 6, 1, 15),
        ...         (2018, 6, 2, 5),
        ...     ],
        ... )
        >>> table = session.read_pandas(
        ...     df, table_name="Origin", default_values={"Year": 0, "Month": 0, "Day": 0}
        ... )
        >>> cube = session.create_cube(table, mode="manual")
        >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
        >>> h["Date"] = [table["Year"], table["Month"], table["Day"]]
        >>> m["Quantity.SUM"] = tt.agg.sum(table["Quantity"])
        >>> m["Average of monthly quantities"] = tt.agg.mean(
        ...     m["Quantity.SUM"], scope=tt.OriginScope(levels={l["Month"]})
        ... )

        :guilabel:`Average of monthly quantities` will evaluate :guilabel:`Quantity.SUM` for each :guilabel:`Month` and average these values "above" this level:

        >>> cube.query(
        ...     m["Quantity.SUM"],
        ...     m["Average of monthly quantities"],
        ...     levels=[l["Day"]],
        ...     include_totals=True,
        ... )
                        Quantity.SUM Average of monthly quantities
        Year  Month Day
        Total                    140                         35.00
        2018                      35                         17.50
              6                   20                         20.00
                    1             15                         15.00
                    2              5                          5.00
              7                   15                         15.00
                    1              5                          5.00
                    2             10                         10.00
        2019                     105                         52.50
              6                   40                         40.00
                    1             25                         25.00
                    2             15                         15.00
              7                   65                         65.00
                    1             15                         15.00
                    2             20                         20.00
                    3             30                         30.00

        The aggregation function can be changed again to compute the max of these averages:

        >>> m["Max average of monthly quantities"] = tt.agg.max(
        ...     m["Average of monthly quantities"],
        ...     scope=tt.OriginScope(levels={l["Year"]}),
        ... )
        >>> cube.query(
        ...     m["Average of monthly quantities"],
        ...     m["Max average of monthly quantities"],
        ...     levels=[l["Year"]],
        ...     include_totals=True,
        ... )
              Average of monthly quantities Max average of monthly quantities
        Year
        Total                         35.00                             52.50
        2018                          17.50                             17.50
        2019                          52.50                             52.50

    """

    levels: Annotated[
        AbstractSet[Identifiable[LevelIdentifier]],
        Field(min_length=1),
        AfterValidator(_check_unique_hierarchies),
    ]
    """The levels constituting the origin of the aggregation."""

    @model_validator(mode="before")
    def _validate(cls, values: Any) -> Any:  # noqa: N805
        if values.kwargs:
            assert not values.args
            return values.kwargs

        warn(
            "The variadic constructor is deprecated, pass a named `levels` parameter instead.",
            category=_DEPRECATED_WARNING_CATEGORY,
            stacklevel=2,
        )
        return {"levels": values.args}

    @override
    def _create_measure_description(
        self, measure: NonConstantMeasureConvertible, /, *, plugin_key: str
    ) -> MeasureDescription:
        return AggregatedMeasure(
            _underlying_measure=measure,
            _plugin_key=plugin_key,
            _on_levels=frozenset(identify(level) for level in self.levels),
        )
