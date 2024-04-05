from __future__ import annotations

from .._measure_convertible import NonConstantMeasureConvertible
from .._measure_description import MeasureDescription, convert_to_measure_description
from .._measures.calculated_measure import CalculatedMeasure, Operator


def ceil(measure: NonConstantMeasureConvertible, /) -> MeasureDescription:
    """Return a measure equal to the smallest integer that is >= to the passed measure.

    Example:
        >>> df = pd.DataFrame(
        ...     columns=["City", "A", "B", "C", "D"],
        ...     data=[
        ...         ("Berlin", 15.0, 10.0, 10.1, 1.0),
        ...         ("London", 24.0, 16.0, 20.5, 3.14),
        ...         ("New York", -27.0, 15.0, 30.7, 10.0),
        ...         ("Paris", 0.0, 0.0, 0.0, 0.0),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, keys=["City"], table_name="Math")
        >>> cube = session.create_cube(table)
        >>> l, m = cube.levels, cube.measures
        >>> m["⌈C⌉"] = tt.math.ceil(m["C.SUM"])
        >>> cube.query(m["C.SUM"], m["⌈C⌉"], levels=[l["City"]])
                  C.SUM ⌈C⌉
        City
        Berlin    10.10  11
        London    20.50  21
        New York  30.70  31
        Paris       .00   0

    """
    return CalculatedMeasure(
        Operator("ceil", [convert_to_measure_description(measure)])
    )
