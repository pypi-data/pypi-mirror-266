from __future__ import annotations

from typing import Literal, Union

from atoti_core import doc

from .._docs_utils import QUANTILE_INDEX_DOC as _QUANTILE_INDEX_DOC
from .._measure_convertible import NonConstantMeasureConvertible
from .._measure_description import MeasureDescription, convert_to_measure_description
from .._measures.generic_measure import GenericMeasure
from ._utils import (
    QUANTILE_STD_AND_VAR_DOC_KWARGS as _QUANTILE_STD_AND_VAR_DOC_KWARGS,
    check_array_type,
)
from .quantile import _Q, _Mode


@doc(_QUANTILE_INDEX_DOC, **_QUANTILE_STD_AND_VAR_DOC_KWARGS)
def quantile_index(
    measure: NonConstantMeasureConvertible,
    /,
    q: Union[_Q, NonConstantMeasureConvertible],
    *,
    mode: _Mode = "inc",
    interpolation: Literal["higher", "lower", "nearest"] = "lower",
) -> MeasureDescription:
    check_array_type(measure)
    return GenericMeasure(
        "CALCULATED_QUANTILE_INDEX",
        mode,
        interpolation,
        [convert_to_measure_description(arg) for arg in [measure, q]],
    )
