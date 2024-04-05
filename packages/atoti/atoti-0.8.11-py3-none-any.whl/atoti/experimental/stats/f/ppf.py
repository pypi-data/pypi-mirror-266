from __future__ import annotations

from typing import Union

from ...._measure_convertible import NonConstantMeasureConvertible
from ...._measure_description import MeasureDescription, convert_to_measure_description
from ...._measures.calculated_measure import CalculatedMeasure, Operator
from .._strictly_positive_number import StrictlyPositiveNumber


def ppf(
    point: NonConstantMeasureConvertible,
    /,
    *,
    numerator_degrees_of_freedom: Union[
        StrictlyPositiveNumber, NonConstantMeasureConvertible
    ],
    denominator_degrees_of_freedom: Union[
        StrictlyPositiveNumber, NonConstantMeasureConvertible
    ],
) -> MeasureDescription:
    """Percent point function for a F-distribution.

    Also called inverse cumulative distribution function.

    Args:
        point: The point where the function is evaluated.
        numerator_degrees_of_freedom: Numerator degrees of freedom.
            Must be positive.
        denominator_degrees_of_freedom: Denominator degrees of freedom.
            Must be positive.

    See Also:
        `The F-distribution Wikipedia page <https://en.wikipedia.org/wiki/F-distribution>`__.

    """
    return CalculatedMeasure(
        Operator(
            "F_ppf",
            [
                convert_to_measure_description(arg)
                for arg in [
                    point,
                    numerator_degrees_of_freedom,
                    denominator_degrees_of_freedom,
                ]
            ],
        )
    )
