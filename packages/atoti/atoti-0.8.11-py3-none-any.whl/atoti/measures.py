from __future__ import annotations

from collections.abc import Iterable, Mapping, Set as AbstractSet
from typing import (
    TYPE_CHECKING,
    Optional,
    Union,
    overload,
)

from atoti_core import MeasureIdentifier
from typing_extensions import override

from ._java_api import JavaApi
from ._local_measures import LocalMeasures
from ._measure_convertible import MeasureConvertible
from ._measure_definition import MeasureDefinition, get_measure_convertible_and_metadata
from ._measure_description import MeasureDescription, convert_to_measure_description
from ._measure_metadata import MeasureMetadata
from .measure import Measure

if TYPE_CHECKING:
    from _typeshed import SupportsKeysAndGetItem  # pylint: disable=nested-import


class Measures(LocalMeasures[Measure]):
    """Manage the :class:`~atoti.Measure` of a :class:`~atoti.Cube`.

    The built-in measure :guilabel:`contributors.COUNT` counts how many facts (i.e. rows) from the cube's base table contributed to each aggregate of a query:

    Example:
        >>> df = pd.DataFrame(
        ...     columns=["ID", "Continent", "Country", "City", "Color"],
        ...     data=[
        ...         (1, "Asia", "Japan", "Tokyo", "red"),
        ...         (2, "Asia", "Japan", "Kyoto", "red"),
        ...         (3, "Asia", "Singapore", "Singapore", "white"),
        ...         (4, "Europe", "Spain", "Madrid", "green"),
        ...         (5, "Europe", "Spain", "Barcelona", "blue"),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, keys=["ID"], table_name="Cities")
        >>> cube = session.create_cube(table, mode="manual")
        >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
        >>> h["ID"] = [table["ID"]]
        >>> cube.query(m["contributors.COUNT"])
          contributors.COUNT
        0                  5
        >>> cube.query(m["contributors.COUNT"], levels=[l["ID"]], include_totals=True)
              contributors.COUNT
        ID
        Total                  5
        1                      1
        2                      1
        3                      1
        4                      1
        5                      1

    The caption of this measure can be changed with :class:`~atoti.I18nConfig`.

    A measure can evaluate to the current member of an expressed level:

    Example:
        >>> h["Color"] = [table["Color"]]
        >>> m["Color"] = l["Color"]
        >>> cube.query(
        ...     m["Color"],
        ...     m["contributors.COUNT"],
        ...     levels=[l["Color"]],
        ...     include_totals=True,
        ... )
               Color contributors.COUNT
        Color
        Total                         5
        blue    blue                  1
        green  green                  1
        red      red                  2
        white  white                  1

    Or, for a multilevel hierarchy:

    Example:
        >>> h["Geography"] = [table["Continent"], table["Country"], table["City"]]
        >>> m["Geography"] = h["Geography"]
        >>> cube.query(
        ...     m["Geography"],
        ...     m["contributors.COUNT"],
        ...     levels=[l["City"]],
        ...     include_totals=True,
        ... )
                                       Geography contributors.COUNT
        Continent Country   City
        Total                                                     5
        Asia                                Asia                  3
                  Japan                    Japan                  2
                            Kyoto          Kyoto                  1
                            Tokyo          Tokyo                  1
                  Singapore            Singapore                  1
                            Singapore  Singapore                  1
        Europe                            Europe                  2
                  Spain                    Spain                  2
                            Barcelona  Barcelona                  1
                            Madrid        Madrid                  1

    A measure can be compared to other objects, such as a constant, a :class:`~atoti.Level`, or another measure.
    If some condition inputs evaluate to ``None``, the resulting measure will evaluate to ``False``:

    Example:
        >>> df = pd.DataFrame(
        ...     columns=["Product", "Quantity", "Threshold"],
        ...     data=[
        ...         ("bag", 5, 1),
        ...         ("car", 1, 5),
        ...         ("laptop", 4, None),
        ...         ("phone", None, 2),
        ...         ("watch", 3, 3),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, keys=["Product"], table_name="Products")
        >>> cube = session.create_cube(table)
        >>> l, m = cube.levels, cube.measures
        >>> m["Condition"] = m["Quantity.SUM"] > m["Threshold.SUM"]
        >>> cube.query(
        ...     m["Quantity.SUM"],
        ...     m["Threshold.SUM"],
        ...     m["Condition"],
        ...     levels=[l["Product"]],
        ...     include_totals=True,
        ... )
                Quantity.SUM Threshold.SUM Condition
        Product
        Total          13.00         11.00      True
        bag             5.00          1.00      True
        car             1.00          5.00     False
        laptop          4.00                   False
        phone                         2.00     False
        watch           3.00          3.00     False

    Measures can be defined and redefined without restarting the cube but, at the moment, deleting a measure will restart the cube so it will be slower:

    Example:
        >>> m["test"] = 13  # no cube restart
        >>> m["test"] = 42  # no cube restart
        >>> del m["test"]  # cube restart

    See Also:
        * :mod:`atoti.agg`, :mod:`atoti.array`, :mod:`atoti.function`, :mod:`atoti.math`, and :mod:`atoti.string` for other ways to define measures.
        * :class:`~atoti.Measure` to configure existing measures.
    """

    def __init__(
        self,
        *,
        cube_name: str,
        java_api: JavaApi,
    ):
        super().__init__(java_api=java_api)

        self._cube_name = cube_name

    def _build_measure(
        self, identifier: MeasureIdentifier, description: JavaApi.JavaMeasureDescription
    ) -> Measure:
        return Measure(
            identifier,
            cube_name=self._cube_name,
            data_type=description.underlying_type,
            description=description.description,
            folder=description.folder,
            formatter=description.formatter,
            java_api=self._java_api,
            visible=description.visible,
        )

    @override
    def _get_underlying(self) -> dict[str, Measure]:
        """Fetch the measures from the JVM each time they are needed."""
        measures = self._java_api.get_measures(self._cube_name)
        return {
            identifier.measure_name: self._build_measure(identifier, measure)
            for identifier, measure in measures.items()
        }

    @override
    def __getitem__(self, key: str, /) -> Measure:
        identifier = MeasureIdentifier(key)
        cube_measure = self._java_api.get_measure(identifier, cube_name=self._cube_name)
        return self._build_measure(identifier, cube_measure)

    # Custom override with same value type as the one used in `update()`.
    @override
    def __setitem__(self, key: str, value: MeasureConvertible, /) -> None:
        self.update({key: value})

    @overload
    def update(
        self,
        __m: SupportsKeysAndGetItem[str, MeasureDefinition],
        **kwargs: MeasureDefinition,
    ) -> None: ...

    @overload
    def update(
        self,
        __m: Iterable[tuple[str, MeasureDefinition]],  # pylint: disable=no-iterable
        **kwargs: MeasureDefinition,
    ) -> None: ...

    @overload
    def update(self, **kwargs: MeasureDefinition) -> None: ...

    @override  # type: ignore[misc]
    # Custom override types on purpose so that measure convertible objects can be inserted.
    def update(  # pyright: ignore[reportInconsistentOverload]
        self,
        __m: Optional[
            Union[
                Mapping[str, MeasureDefinition],
                Iterable[tuple[str, MeasureDefinition]],  # pylint: disable=no-iterable
            ]
        ] = None,
        **kwargs: MeasureDefinition,
    ) -> None:
        other: dict[str, MeasureDefinition] = {}

        if __m is not None:
            other.update(__m)
        other.update(**kwargs)

        self._update(
            {
                measure_name: get_measure_convertible_and_metadata(measure_definition)
                for measure_name, measure_definition in other.items()
            }
        )

    @override
    # Custom override types on purpose so that measure-like objects can be inserted.
    def _update(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: Mapping[str, tuple[MeasureConvertible, MeasureMetadata]],  # type: ignore[override]
    ) -> None:
        for measure_name, (
            measure,
            measure_metadata,
        ) in other.items():
            if not isinstance(measure, MeasureDescription):
                measure = convert_to_measure_description(measure)  # noqa: PLW2901

            try:
                measure._distil(
                    MeasureIdentifier(measure_name),
                    cube_name=self._cube_name,
                    java_api=self._java_api,
                    measure_metadata=measure_metadata,
                )
            except AttributeError as err:
                raise ValueError(f"Cannot create a measure from {measure}") from err

        self._java_api.publish_measures(self._cube_name)

    @override
    def _delete_keys(self, keys: AbstractSet[str], /) -> None:
        for key in keys:
            self._java_api.delete_measure(
                MeasureIdentifier(key), cube_name=self._cube_name
            )
