from __future__ import annotations

from typing import Union

from ...._measure_convertible import NonConstantMeasureConvertible
from ...._measure_description import MeasureDescription, convert_to_measure_description
from ...._measures.calculated_measure import CalculatedMeasure, Operator
from .._numeric_measure_convertible import NumericMeasureConvertible
from .._strictly_positive_number import StrictlyPositiveNumber


def pdf(
    point: NonConstantMeasureConvertible,
    /,
    *,
    mean: NumericMeasureConvertible = 0,
    standard_deviation: Union[
        StrictlyPositiveNumber, NonConstantMeasureConvertible
    ] = 1,
) -> MeasureDescription:
    r"""Probability density function for a normal distribution.

    The pdf is given by the formula

    .. math::

        \operatorname {pdf}(x) = \frac{1}{ \sigma \sqrt{2 \pi} } e^{-\frac{1}{2} \left(\frac{x - \mu}{\sigma}\right)^{2}}

    Where :math:`\mu` is the mean (or expectation) of the distribution while :math:`\sigma` is its standard deviation.

    Args:
        point: The point where the function is evaluated.
        mean: The mean value of the distribution.
        standard_deviation: The standard deviation of the distribution.
            Must be positive.

    See Also:
        `General normal distribution <https://en.wikipedia.org/wiki/Normal_distribution#General_normal_distribution>`__.

    """
    return CalculatedMeasure(
        Operator(
            "normal_density",
            [
                convert_to_measure_description(arg)
                for arg in [point, mean, standard_deviation]
            ],
        )
    )
