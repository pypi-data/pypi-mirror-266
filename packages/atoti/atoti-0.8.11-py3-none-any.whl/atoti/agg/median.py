from __future__ import annotations

from typing import Optional, Union, overload

from atoti_core import doc

from .._measure_convertible import NonConstantMeasureConvertible
from .._measure_description import MeasureDescription
from ..scope._scope import Scope
from ._utils import (
    BASIC_ARGS_DOC as _BASIC_ARGS_DOC,
    BASIC_DOC as _BASIC_DOC,
    NonConstantColumnConvertibleOrLevel,
)
from .quantile import quantile


@overload
def median(operand: NonConstantColumnConvertibleOrLevel, /) -> MeasureDescription: ...


@overload
def median(
    operand: NonConstantMeasureConvertible, /, *, scope: Scope
) -> MeasureDescription: ...


@doc(
    _BASIC_DOC,
    args=_BASIC_ARGS_DOC,
    value="median",
    example="""
        >>> m["Median Price"] = tt.agg.median(table["Price"])
        >>> cube.query(m["Median Price"])
          Median Price
        0        25.90""".replace("\n", "", 1),
)
def median(
    operand: Union[NonConstantColumnConvertibleOrLevel, NonConstantMeasureConvertible],
    /,
    *,
    scope: Optional[Scope] = None,
) -> MeasureDescription:
    # The type checkers cannot see that the `@overload` above ensure that this call is valid.
    return quantile(operand, q=0.5, scope=scope)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
