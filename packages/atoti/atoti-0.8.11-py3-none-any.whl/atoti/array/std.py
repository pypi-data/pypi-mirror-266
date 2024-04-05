from __future__ import annotations

from atoti_core import doc

from .._docs_utils import (
    STD_AND_VAR_DOC as _STD_AND_VAR_DOC,
    STD_DOC_KWARGS as _STD_DOC_KWARGS,
)
from .._measure_convertible import MeasureOperation, NonConstantMeasureConvertible
from ..math import sqrt
from ._utils import (
    QUANTILE_STD_AND_VAR_DOC_KWARGS as _QUANTILE_STD_AND_VAR_DOC_KWARGS,
    check_array_type,
)
from .var import _Mode, var


@doc(
    _STD_AND_VAR_DOC,
    **_STD_DOC_KWARGS,
    **_QUANTILE_STD_AND_VAR_DOC_KWARGS,
)
def std(
    measure: NonConstantMeasureConvertible,
    /,
    *,
    mode: _Mode = "sample",
) -> MeasureOperation:
    check_array_type(measure)
    return sqrt(var(measure, mode=mode))
