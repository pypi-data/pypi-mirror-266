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
def long(operand: NonConstantColumnConvertibleOrLevel, /) -> MeasureDescription: ...


@overload
def long(
    operand: NonConstantMeasureConvertible, /, *, scope: Scope
) -> MeasureDescription: ...


@doc(
    _BASIC_DOC,
    args=_BASIC_ARGS_DOC,
    value="sum of the positive values",
    example="""
        >>> m["Quantity.LONG"] = tt.agg.long(table["Quantity"])
        >>> cube.query(m["Quantity.LONG"])
          Quantity.LONG
        0         1,110""".replace("\n", "", 1),
)
def long(
    operand: Union[NonConstantColumnConvertibleOrLevel, NonConstantMeasureConvertible],
    /,
    *,
    scope: Optional[Scope] = None,
) -> MeasureDescription:
    # The type checkers cannot see that the `@overload` above ensure that this call is valid.
    return agg(operand, plugin_key="LONG", scope=scope)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
