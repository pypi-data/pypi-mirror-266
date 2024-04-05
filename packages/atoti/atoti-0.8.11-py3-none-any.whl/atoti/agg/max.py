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
def max(  # noqa: A001
    operand: NonConstantColumnConvertibleOrLevel,
    /,
) -> MeasureDescription: ...


@overload
def max(  # noqa: A001
    operand: NonConstantMeasureConvertible, /, *, scope: Scope
) -> MeasureDescription: ...


@doc(
    _BASIC_DOC,
    args=_BASIC_ARGS_DOC,
    value="maximum",
    example="""
        >>> m["Maximum Price"] = tt.agg.max(table["Price"])
        >>> cube.query(m["Maximum Price"])
          Maximum Price
        0         43.00""".replace("\n", "", 1),
)
def max(  # noqa: A001
    operand: Union[NonConstantColumnConvertibleOrLevel, NonConstantMeasureConvertible],
    /,
    *,
    scope: Optional[Scope] = None,
) -> MeasureDescription:
    # The type checkers cannot see that the `@overload` above ensure that this call is valid.
    return agg(operand, plugin_key="MAX", scope=scope)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
