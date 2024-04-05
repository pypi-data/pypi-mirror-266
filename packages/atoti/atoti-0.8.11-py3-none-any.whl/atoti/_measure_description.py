from __future__ import annotations

import math
from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional, cast

from atoti_core import (
    ArithmeticOperation,
    CombinedCondition,
    ComparisonCondition,
    Condition,
    Constant,
    HasIdentifier,
    HierarchyIdentifier,
    HierarchyIsinCondition,
    Identifier,
    IndexingOperation,
    IsinCondition,
    LevelIdentifier,
    MeasureIdentifier,
    Operation,
    keyword_only_dataclass,
)
from typing_extensions import override

from ._java_api import JavaApi
from ._measure_convertible import MeasureConvertible, MeasureOperand
from ._measure_metadata import MeasureMetadata


@keyword_only_dataclass
@dataclass(eq=False, frozen=True)
class MeasureDescription(Operation[MeasureIdentifier]):
    """The description of a :class:`~atoti.Measure` that has not been added to the cube yet."""

    def _distil(
        self,
        identifier: Optional[MeasureIdentifier] = None,
        /,
        *,
        java_api: JavaApi,
        cube_name: str,
        measure_metadata: Optional[MeasureMetadata] = None,
    ) -> MeasureIdentifier:
        """Return the identifier of the measure, creating it in the cube if it does not exist yet."""
        name: Optional[str] = self.__dict__.get("_name")
        if not name:
            name = self._do_distil(
                identifier,
                java_api=java_api,
                cube_name=cube_name,
                measure_metadata=measure_metadata,
            ).measure_name
            self.__dict__["_name"] = name
        elif identifier:
            # This measure has already been distilled, this is a copy with a different name.
            java_api.copy_measure(
                MeasureIdentifier(name),
                identifier,
                cube_name=cube_name,
                measure_metadata=measure_metadata,
            )
        assert isinstance(name, str)
        return MeasureIdentifier(name)

    @abstractmethod
    def _do_distil(
        self,
        identifier: Optional[MeasureIdentifier] = None,
        /,
        *,
        java_api: JavaApi,
        cube_name: str,
        measure_metadata: Optional[MeasureMetadata] = None,
    ) -> MeasureIdentifier:
        """Create the measure in the cube and return its identifier."""

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        return frozenset([MeasureIdentifier])


def convert_operand_to_measure_description(
    value: Optional[MeasureOperand], /
) -> MeasureDescription:
    # pylint: disable=nested-import
    from ._measures.level_measure import LevelMeasure
    from ._measures.published_measure import PublishedMeasure

    # pylint: enable=nested-import

    if value is None:
        raise TypeError(
            f"Cannot convert `{value}` operand to `{MeasureDescription.__name__}`."
        )

    if isinstance(value, LevelIdentifier):
        return LevelMeasure(value)

    if isinstance(value, MeasureIdentifier):
        return PublishedMeasure(value.measure_name)

    return convert_to_measure_description(
        value.value if isinstance(value, Constant) else cast(MeasureConvertible, value)
    )


def convert_to_measure_description(  # noqa: C901, PLR0911, PLR0912
    value: MeasureConvertible,
    /,
) -> MeasureDescription:
    # pylint: disable=nested-import
    from ._measures.boolean_measure import BooleanMeasure
    from ._measures.calculated_measure import CalculatedMeasure, Operator
    from ._measures.constant_measure import ConstantMeasure
    from ._measures.hierarchy_measure import HierarchyMeasure
    from ._measures.level_measure import LevelMeasure
    from ._measures.published_measure import PublishedMeasure

    # pylint: enable=nested-import

    if isinstance(value, MeasureDescription):
        return value

    if isinstance(value, Condition):
        if isinstance(value, CombinedCondition):
            return BooleanMeasure(
                value.boolean_operator,
                tuple(
                    convert_to_measure_description(operand)
                    for operand in value.sub_conditions
                ),
            )

        if isinstance(value, ComparisonCondition):
            assert not isinstance(
                value.subject, HierarchyIdentifier
            ), f"Instances of `{HierarchyIsinCondition.__name__}` should have been converted to combined `{ComparisonCondition.__name__}`s."

            subject = convert_operand_to_measure_description(value.subject)
            if value.target is None:
                return BooleanMeasure(
                    "isNull" if value.operator == "eq" else "notNull",
                    (subject,),
                )
            return BooleanMeasure(
                value.operator,
                (
                    subject,
                    convert_operand_to_measure_description(value.target),
                ),
            )

        if isinstance(value, (HierarchyIsinCondition, IsinCondition)):
            return convert_to_measure_description(value.combined_comparison_condition)

        raise TypeError(f"Unexpected condition type: `{type(value)}`.")

    if isinstance(value, HasIdentifier):
        identifier = value._identifier

        if isinstance(identifier, LevelIdentifier):
            return LevelMeasure(identifier)

        if isinstance(identifier, HierarchyIdentifier):
            return HierarchyMeasure(identifier)

        assert isinstance(identifier, MeasureIdentifier)
        return PublishedMeasure(identifier.measure_name)

    if isinstance(value, Operation):
        if isinstance(value, ArithmeticOperation):
            return CalculatedMeasure(
                Operator(
                    value.operator,
                    [
                        convert_operand_to_measure_description(operand)
                        for operand in value.operands
                    ],
                )
            )

        if isinstance(value, IndexingOperation):
            if isinstance(value.index, slice):
                if value.index.step:
                    raise ValueError(
                        "Cannot index an array measure using a slice with a step."
                    )
                start = value.index.start if value.index.start is not None else 0
                stop = value.index.stop if value.index.stop is not None else math.inf
                return CalculatedMeasure(
                    Operator(
                        "vector_sub",
                        [
                            convert_operand_to_measure_description(value.operand),
                            convert_to_measure_description(start),
                            convert_to_measure_description(stop),
                        ],
                    )
                )

            return CalculatedMeasure(
                Operator(
                    "vector_element",
                    [
                        convert_operand_to_measure_description(value.operand),
                        convert_operand_to_measure_description(value.index),
                    ],
                )
            )

        raise TypeError(f"Unexpected operation type: `{type(value)}`.")

    return ConstantMeasure(
        _value=Constant(
            # Until 0.9.0, tuples are not valid constants, lists are.
            # See comment explaining why in `atoti_core.constant`.
            list(value) if isinstance(value, tuple) else value
        ),
    )
