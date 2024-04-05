from __future__ import annotations

from typing import Optional, Union, overload

from atoti_core import doc

from .._docs_utils import (
    STD_AND_VAR_DOC as _STD_AND_VAR_DOC,
    STD_DOC_KWARGS as _STD_DOC_KWARGS,
)
from .._measure_convertible import NonConstantMeasureConvertible
from .._measure_description import MeasureDescription
from ..array.var import _Mode
from ..math import sqrt
from ..scope._scope import Scope
from ._utils import (
    QUANTILE_STD_AND_VAR_DOC_KWARGS as _QUANTILE_STD_AND_VAR_DOC_KWARGS,
    SCOPE_DOC as _SCOPE_DOC,
    NonConstantColumnConvertibleOrLevel,
)
from .var import var


@overload
def std(
    operand: NonConstantColumnConvertibleOrLevel,
    /,
    *,
    mode: _Mode = ...,
) -> MeasureDescription: ...


@overload
def std(
    operand: NonConstantMeasureConvertible,
    /,
    *,
    mode: _Mode = ...,
    scope: Scope,
) -> MeasureDescription: ...


@doc(
    _STD_AND_VAR_DOC,
    _SCOPE_DOC,
    **_STD_DOC_KWARGS,
    **_QUANTILE_STD_AND_VAR_DOC_KWARGS,
)
def std(
    operand: Union[NonConstantColumnConvertibleOrLevel, NonConstantMeasureConvertible],
    /,
    *,
    mode: _Mode = "sample",
    scope: Optional[Scope] = None,
) -> MeasureDescription:
    return sqrt(  # type: ignore[return-value] # pyright: ignore[reportReturnType]
        # The type checkers cannot see that the `@overload` above ensure that this call is valid.
        var(operand, mode=mode, scope=scope)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
    )
