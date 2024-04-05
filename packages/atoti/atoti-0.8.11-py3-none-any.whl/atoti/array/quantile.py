from __future__ import annotations

from typing import Annotated, Literal, Union

from atoti_core import doc
from pydantic import Field

from .._docs_utils import QUANTILE_DOC as _QUANTILE_DOC
from .._measure_convertible import NonConstantMeasureConvertible
from .._measure_description import MeasureDescription, convert_to_measure_description
from .._measures.generic_measure import GenericMeasure
from ._utils import (
    QUANTILE_STD_AND_VAR_DOC_KWARGS as _QUANTILE_STD_AND_VAR_DOC_KWARGS,
    check_array_type,
)

_Interpolation = Literal["linear", "higher", "lower", "nearest", "midpoint"]
_Mode = Literal["simple", "centered", "inc", "exc"]


_Q = Annotated[float, Field(ge=0, le=1)]


@doc(_QUANTILE_DOC, **_QUANTILE_STD_AND_VAR_DOC_KWARGS)
def quantile(
    measure: NonConstantMeasureConvertible,
    /,
    q: Union[_Q, NonConstantMeasureConvertible],
    *,
    mode: _Mode = "inc",
    interpolation: _Interpolation = "linear",
) -> MeasureDescription:
    check_array_type(measure)
    return GenericMeasure(
        "CALCULATED_QUANTILE",
        mode,
        interpolation,
        [convert_to_measure_description(arg) for arg in [measure, q]],
    )
