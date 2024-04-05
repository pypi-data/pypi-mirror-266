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
def short(operand: NonConstantColumnConvertibleOrLevel, /) -> MeasureDescription: ...


@overload
def short(
    operand: NonConstantMeasureConvertible, /, *, scope: Scope
) -> MeasureDescription: ...


@doc(
    _BASIC_DOC,
    args=_BASIC_ARGS_DOC,
    value="sum of the negative values",
    example="""
        >>> m["Quantity.SHORT"] = tt.agg.short(table["Quantity"])
        >>> cube.query(m["Quantity.SHORT"])
          Quantity.SHORT
        0              0""".replace("\n", "", 1),
)
def short(
    operand: Union[NonConstantColumnConvertibleOrLevel, NonConstantMeasureConvertible],
    /,
    *,
    scope: Optional[Scope] = None,
) -> MeasureDescription:
    # The type checkers cannot see that the `@overload` above ensure that this call is valid.
    return agg(operand, plugin_key="SHORT", scope=scope)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
