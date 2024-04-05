from __future__ import annotations

from typing import Optional, Union, overload

from ..._measure_convertible import NonConstantMeasureConvertible
from ..._measure_description import MeasureDescription
from ...agg._agg import agg
from ...agg._utils import NonConstantColumnConvertibleOrLevel
from ...scope._scope import Scope


@overload
def distinct(operand: NonConstantColumnConvertibleOrLevel, /) -> MeasureDescription: ...


@overload
def distinct(
    operand: NonConstantMeasureConvertible,
    /,
    *,
    scope: Scope,
) -> MeasureDescription: ...


def distinct(
    operand: Union[NonConstantColumnConvertibleOrLevel, NonConstantMeasureConvertible],
    /,
    *,
    scope: Optional[Scope] = None,
) -> MeasureDescription:
    """Return an array measure representing the distinct values of the passed measure."""
    # The type checkers cannot see that the `@overload` above ensure that this call is valid.
    return agg(operand, plugin_key="DISTINCT", scope=scope)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
