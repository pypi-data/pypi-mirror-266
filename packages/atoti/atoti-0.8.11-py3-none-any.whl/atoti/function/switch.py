from __future__ import annotations

from collections.abc import Mapping, Set as AbstractSet
from functools import reduce
from typing import Optional, Union
from warnings import warn

from atoti_core import (
    DEPRECATED_WARNING_CATEGORY,
    ComparisonCondition,
    Condition,
    Constant,
    ConstantValue,
    HasIdentifier,
    LevelIdentifier,
    Operation,
    is_constant_value,
)

from .._measure_convertible import (
    MeasureCondition,
    MeasureConvertible,
    MeasureConvertibleIdentifier,
    MeasureOperation,
    NonConstantMeasureConvertible,
)
from .._measure_description import MeasureDescription, convert_to_measure_description
from .._measures.switch_on_measure import SwitchOnMeasure
from .where import where


def _create_eq_condition(
    *,
    subject: NonConstantMeasureConvertible,
    target: Optional[MeasureConvertible],
) -> MeasureCondition:
    if isinstance(subject, Condition):
        raise TypeError(
            f"Cannot use a `{type(subject).__name__}` as a `{switch.__name__}()` subject."
        )

    condition_target: Optional[
        Union[
            Constant,
            MeasureConvertibleIdentifier,
            MeasureOperation,
        ]
    ] = None

    if target is not None:
        if isinstance(target, Condition):
            raise TypeError(
                f"Cannot use a `{type(target).__name__}` `{switch.__name__}()` target."
            )

        if isinstance(target, HasIdentifier):
            condition_target = target._identifier
        elif isinstance(target, Operation):
            condition_target = target
        else:
            condition_target = Constant(target)

    return ComparisonCondition(
        subject=subject._identifier if isinstance(subject, HasIdentifier) else subject,
        operator="eq",
        target=condition_target,
    )


def switch(
    subject: NonConstantMeasureConvertible,
    cases: Mapping[
        Union[
            Optional[MeasureConvertible],
            AbstractSet[Optional[MeasureConvertible]],
            tuple[Optional[MeasureConvertible], ...],
        ],
        MeasureConvertible,
    ],
    /,
    *,
    default: Optional[MeasureConvertible] = None,
) -> MeasureDescription:
    """Return a measure equal to the value of the first case for which *subject* is equal to the case's key.

    *cases*'s values and *default* must either be all numerical, all boolean or all objects.

    Args:
        subject: The measure or level to compare to *cases*' keys.
        cases: A mapping from keys to compare with *subject* to the values to return if the comparison is ``True``.
        default: The measure to use when none of the *cases* matched.

    Example:
        >>> df = pd.DataFrame(
        ...     columns=["Id", "City", "Value"],
        ...     data=[
        ...         (0, "Paris", 1.0),
        ...         (1, "Paris", 2.0),
        ...         (2, "London", 3.0),
        ...         (3, "London", 4.0),
        ...         (4, "Paris", 5.0),
        ...         (5, "Singapore", 7.0),
        ...         (6, "NYC", 2.0),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, keys=["Id"], table_name="Switch example")
        >>> cube = session.create_cube(table)
        >>> l, m = cube.levels, cube.measures
        >>> m["Continent"] = tt.switch(
        ...     l["City"],
        ...     {
        ...         frozenset({"Paris", "London"}): "Europe",
        ...         "Singapore": "Asia",
        ...         "NYC": "North America",
        ...     },
        ... )
        >>> cube.query(m["Continent"], levels=[l["City"]])
                       Continent
        City
        London            Europe
        NYC        North America
        Paris             Europe
        Singapore           Asia
        >>> m["Europe & Asia value"] = tt.agg.sum(
        ...     tt.switch(
        ...         m["Continent"],
        ...         {frozenset({"Europe", "Asia"}): m["Value.SUM"]},
        ...         default=0.0,
        ...     ),
        ...     scope=tt.OriginScope(levels={l["Id"], l["City"]}),
        ... )
        >>> cube.query(m["Europe & Asia value"], levels=[l["City"]])
                  Europe & Asia value
        City
        London                   7.00
        NYC                       .00
        Paris                    8.00
        Singapore                7.00
        >>> cube.query(m["Europe & Asia value"])
          Europe & Asia value
        0               22.00

    See Also:
        :func:`atoti.where`.
    """
    if any(isinstance(key, tuple) for key in cases):
        warn(
            "Passing a tuple as a case key is deprecated. Pass a frozenset instead.",
            category=DEPRECATED_WARNING_CATEGORY,
            stacklevel=1,
        )

    if (
        isinstance(subject, HasIdentifier)
        and isinstance(subject._identifier, LevelIdentifier)
        and default is not None
    ):
        flatten_cases: dict[Optional[MeasureConvertible], MeasureConvertible] = {}

        for key, value in cases.items():
            if isinstance(key, (AbstractSet, tuple)):
                for element in key:
                    flatten_cases[element] = value
            else:
                flatten_cases[key] = value

        constant_cases: dict[Optional[ConstantValue], MeasureConvertible] = {
            key: value
            for key, value in flatten_cases.items()
            if key is None or is_constant_value(key)
        }

        if len(constant_cases) == len(flatten_cases):
            return SwitchOnMeasure(
                _subject=subject._identifier,
                _cases={
                    key: convert_to_measure_description(value)
                    for key, value in constant_cases.items()
                    if key is not None
                },
                _default=convert_to_measure_description(default),
                _above_level=convert_to_measure_description(cases[None])
                if None in cases
                else None,
            )

        # If the subject is a measure, we return a where measure
    condition_to_measure: dict[
        NonConstantMeasureConvertible,
        MeasureConvertible,
    ] = {}
    for values, measure in cases.items():
        if isinstance(values, (AbstractSet, tuple)):
            condition_to_measure[
                reduce(
                    lambda a, b: a | b,  # pyright: ignore[reportUnknownLambdaType]
                    [
                        _create_eq_condition(subject=subject, target=value)
                        for value in values
                    ],
                )
            ] = measure
        else:
            condition_to_measure[
                _create_eq_condition(subject=subject, target=values)
            ] = measure
    return where(condition_to_measure, default=default)
