from __future__ import annotations

from typing import Optional, Union, overload

from .._measure_convertible import NonConstantMeasureConvertible
from .._measure_description import MeasureDescription
from ..scope._scope import Scope
from ._agg import agg
from ._utils import NonConstantColumnConvertibleOrLevel


@overload
def count(operand: NonConstantColumnConvertibleOrLevel, /) -> MeasureDescription: ...


@overload
def count(
    operand: NonConstantMeasureConvertible, /, *, scope: Scope
) -> MeasureDescription: ...


def count(
    operand: Union[NonConstantColumnConvertibleOrLevel, NonConstantMeasureConvertible],
    /,
    *,
    scope: Optional[Scope] = None,
) -> MeasureDescription:
    """Return a measure equal to the number of aggregated elements.

    See Also:
        :func:`atoti.agg.count_distinct`.
    """
    # The type checkers cannot see that the `@overload` above ensure that this call is valid.
    return agg(operand, plugin_key="COUNT", scope=scope)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
