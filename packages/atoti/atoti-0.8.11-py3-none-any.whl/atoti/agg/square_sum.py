from __future__ import annotations

from typing import Optional, Union, overload

from atoti_core import doc

from .._measure_convertible import NonConstantMeasureConvertible
from .._measure_description import MeasureDescription
from ..scope._scope import Scope
from ._agg import agg
from ._utils import (
    BASIC_ARGS_DOC as _BASIC_ARGS_DOC,
    BASIC_DOC as _BASIC_DOC,
    NonConstantColumnConvertibleOrLevel,
)


@overload
def square_sum(
    operand: NonConstantColumnConvertibleOrLevel, /
) -> MeasureDescription: ...


@overload
def square_sum(
    operand: NonConstantMeasureConvertible, /, *, scope: Scope
) -> MeasureDescription: ...


@doc(
    _BASIC_DOC,
    args=_BASIC_ARGS_DOC,
    value="sum of the square",
    example="""
        >>> m["Other.SQUARE_SUM"] = tt.agg.square_sum(table["Other"])
        >>> cube.query(m["Other.SQUARE_SUM"])
          Other.SQUARE_SUM
        0                9""".replace("\n", "", 1),
)
def square_sum(
    operand: Union[NonConstantColumnConvertibleOrLevel, NonConstantMeasureConvertible],
    /,
    *,
    scope: Optional[Scope] = None,
) -> MeasureDescription:
    # The type checkers cannot see that the `@overload` above ensure that this call is valid.
    return agg(operand, plugin_key="SQ_SUM", scope=scope)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
