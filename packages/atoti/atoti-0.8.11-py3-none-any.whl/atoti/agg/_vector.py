from __future__ import annotations

from typing import Optional, Union, overload

from .._measure_convertible import NonConstantMeasureConvertible
from .._measure_description import MeasureDescription
from ..scope._scope import Scope
from ._agg import agg
from ._utils import NonConstantColumnConvertibleOrLevel


@overload
def vector(operand: NonConstantColumnConvertibleOrLevel, /) -> MeasureDescription: ...


@overload
def vector(
    operand: NonConstantMeasureConvertible, /, *, scope: Scope
) -> MeasureDescription: ...


def vector(
    operand: Union[NonConstantColumnConvertibleOrLevel, NonConstantMeasureConvertible],
    /,
    *,
    scope: Optional[Scope] = None,
) -> MeasureDescription:
    """Return an array measure representing the values of the passed operand across the specified scope."""
    # The type checkers cannot see that the `@overload` above ensure that this call is valid.
    return agg(operand, plugin_key="VECTOR", scope=scope)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
