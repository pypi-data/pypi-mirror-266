from __future__ import annotations

from typing import Optional, Union, cast, overload

from atoti_core import ColumnIdentifier, HasIdentifier

from .._measure_convertible import NonConstantMeasureConvertible
from .._measure_description import MeasureDescription
from .._measures.calculated_measure import AggregatedMeasure
from .._measures.column_measure import ColumnMeasure
from .._measures.level_measure import LevelMeasure
from .._measures.udaf_measure import UdafMeasure
from ..scope._scope import Scope
from ._utils import (
    NonConstantColumnConvertibleOrLevel,
    is_non_constant_column_convertible_or_level,
)


@overload
def agg(
    operand: NonConstantColumnConvertibleOrLevel,
    /,
    *,
    plugin_key: str,
) -> MeasureDescription: ...


@overload
def agg(
    operand: NonConstantMeasureConvertible,
    /,
    *,
    plugin_key: str,
    scope: Scope,
) -> MeasureDescription: ...


def agg(
    operand: Union[NonConstantColumnConvertibleOrLevel, NonConstantMeasureConvertible],
    /,
    *,
    plugin_key: str,
    scope: Optional[Scope] = None,
) -> MeasureDescription:
    if is_non_constant_column_convertible_or_level(operand):
        if scope:
            raise ValueError(
                "The passed operand has an intrinsic scope, no other scope can be specified."
            )

        if isinstance(operand, HasIdentifier):
            identifier = operand._identifier

            return (
                ColumnMeasure(
                    _column_identifier=identifier,
                    _plugin_key=plugin_key,
                )
                if isinstance(identifier, ColumnIdentifier)
                else AggregatedMeasure(
                    _underlying_measure=LevelMeasure(
                        # Pyright is able to check that `identifier` is of type `LevelIdentifier` but mypy cannot.
                        identifier,  # type: ignore[arg-type]
                    ),
                    _plugin_key=plugin_key,
                    _on_levels=[
                        # Pyright is able to check that `identifier` is of type `LevelIdentifier` but mypy cannot.
                        identifier,  # type: ignore[list-item]
                    ],
                )
            )

        return UdafMeasure(_plugin_key=plugin_key, _operation=operand)

    operand = cast(NonConstantMeasureConvertible, operand)

    if not scope:
        raise ValueError("The passed operand requires a scope to be specified.")

    return scope._create_measure_description(operand, plugin_key=plugin_key)
