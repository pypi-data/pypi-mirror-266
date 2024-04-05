from __future__ import annotations

from typing import Optional, Union, overload

from atoti_core import doc

from .._docs_utils import QUANTILE_DOC as _QUANTILE_DOC
from .._measure_convertible import NonConstantMeasureConvertible
from .._measure_description import MeasureDescription
from ..array import quantile as array_quantile
from ..array.quantile import _Q, _Interpolation, _Mode
from ..scope._scope import Scope
from ._utils import (
    QUANTILE_STD_AND_VAR_DOC_KWARGS as _QUANTILE_STD_AND_VAR_DOC_KWARGS,
    SCOPE_DOC as _SCOPE_DOC,
    NonConstantColumnConvertibleOrLevel,
)
from ._vector import vector


@overload
def quantile(
    operand: NonConstantColumnConvertibleOrLevel,
    /,
    q: Union[_Q, NonConstantMeasureConvertible],
    *,
    mode: _Mode = ...,
    interpolation: _Interpolation = ...,
) -> MeasureDescription: ...


@overload
def quantile(
    operand: NonConstantMeasureConvertible,
    /,
    q: Union[_Q, NonConstantMeasureConvertible],
    *,
    mode: _Mode = ...,
    interpolation: _Interpolation = ...,
    scope: Scope,
) -> MeasureDescription: ...


@doc(_QUANTILE_DOC, _SCOPE_DOC, **_QUANTILE_STD_AND_VAR_DOC_KWARGS)
def quantile(
    operand: Union[NonConstantColumnConvertibleOrLevel, NonConstantMeasureConvertible],
    /,
    q: Union[_Q, NonConstantMeasureConvertible],
    *,
    mode: _Mode = "inc",
    interpolation: _Interpolation = "linear",
    scope: Optional[Scope] = None,
) -> MeasureDescription:
    return array_quantile(
        # The type checkers cannot see that the `@overload` above ensure that this call is valid.
        vector(operand, scope=scope),  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
        q=q,
        mode=mode,
        interpolation=interpolation,
    )
