from __future__ import annotations

from typing import Optional, Union

from atoti_core import (
    Condition,
    ConditionBound,
    ConditionCombinationOperatorBound,
    ConditionComparisonOperatorBound,
    Constant,
    ConstantValue,
    HasIdentifier,
    HierarchyIdentifier,
    LevelIdentifier,
    MeasureIdentifier,
    Operation,
    OperationBound,
    is_constant_value,
)
from typing_extensions import TypeGuard

MeasureConvertibleIdentifier = Union[
    HierarchyIdentifier, LevelIdentifier, MeasureIdentifier
]

MeasureOperation = Operation[MeasureConvertibleIdentifier]

MeasureCondition = Condition[
    Union[HierarchyIdentifier, MeasureConvertibleIdentifier, MeasureOperation],
    ConditionComparisonOperatorBound,
    Optional[
        Union[
            Constant,
            MeasureConvertibleIdentifier,
            MeasureOperation,
        ]
    ],
    ConditionCombinationOperatorBound,
]


MeasureConditionOrOperation = Union[MeasureCondition, MeasureOperation]

NonConstantMeasureOperand = Union[
    MeasureConditionOrOperation, MeasureConvertibleIdentifier
]
MeasureOperand = Union[Constant, NonConstantMeasureOperand]

NonConstantMeasureConvertible = Union[
    HasIdentifier[MeasureConvertibleIdentifier], MeasureConditionOrOperation
]

MeasureConvertible = Union[ConstantValue, NonConstantMeasureConvertible]


def _is_measure_base_operation(value: Union[ConditionBound, OperationBound], /) -> bool:
    # It is not a measure `BaseOperation` if there are some unexpected identifier types.
    return not (
        value._identifier_types
        - {HierarchyIdentifier, LevelIdentifier, MeasureIdentifier}
    )


def is_measure_condition(value: object, /) -> TypeGuard[MeasureCondition]:
    return isinstance(value, Condition) and _is_measure_base_operation(value)


def is_measure_operation(value: object, /) -> TypeGuard[MeasureOperation]:
    return isinstance(value, Operation) and _is_measure_base_operation(value)


def is_measure_condition_or_operation(
    value: object, /
) -> TypeGuard[MeasureConditionOrOperation]:
    return (
        is_measure_condition(value)
        if isinstance(value, Condition)
        else is_measure_operation(value)
    )


def is_non_constant_measure_convertible(
    value: object, /
) -> TypeGuard[NonConstantMeasureConvertible]:
    return (
        isinstance(
            value._identifier,
            (HierarchyIdentifier, LevelIdentifier, MeasureIdentifier),
        )
        if isinstance(value, HasIdentifier)
        else is_measure_condition_or_operation(value)
    )


def is_measure_convertible(value: object, /) -> TypeGuard[MeasureConvertible]:
    return (
        is_non_constant_measure_convertible(value)
        if isinstance(value, (Condition, HasIdentifier, Operation))
        else is_constant_value(value)
    )
