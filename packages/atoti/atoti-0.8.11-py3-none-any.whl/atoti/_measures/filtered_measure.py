from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal, Optional, Union

from atoti_core import (
    Condition,
    ConditionComparisonOperatorBound,
    Constant,
    DataType,
    HierarchyIdentifier,
    LevelIdentifier,
    MeasureIdentifier,
    decombine_condition,
    is_primitive_type,
    keyword_only_dataclass,
)
from typing_extensions import override

from .._java_api import JavaApi
from .._measure_description import MeasureDescription
from .._measure_metadata import MeasureMetadata
from .._py4j_utils import to_java_list, to_java_object


def is_object_type(data_type: DataType, /) -> bool:
    return not is_primitive_type(data_type)


@keyword_only_dataclass
@dataclass(eq=False, frozen=True)
class WhereMeasure(MeasureDescription):
    """A measure that returns the value of other measures based on conditions."""

    _measure_to_conditions: Mapping[MeasureDescription, tuple[MeasureDescription, ...]]
    _default_measure: Optional[MeasureDescription]

    @override
    def _do_distil(
        self,
        identifier: Optional[MeasureIdentifier] = None,
        /,
        *,
        java_api: JavaApi,
        cube_name: str,
        measure_metadata: Optional[MeasureMetadata] = None,
    ) -> MeasureIdentifier:
        underlying_measure_to_conditions = {
            measure._distil(
                java_api=java_api, cube_name=cube_name
            ).measure_name: conditions
            for measure, conditions in self._measure_to_conditions.items()
        }
        underlying_default_measure = (
            self._default_measure._distil(
                java_api=java_api, cube_name=cube_name
            ).measure_name
            if self._default_measure is not None
            else None
        )

        return java_api.create_measure(
            identifier,
            "WHERE",
            {
                measure: [
                    condition._distil(
                        java_api=java_api, cube_name=cube_name
                    ).measure_name
                    for condition in conditions
                ]
                for measure, conditions in underlying_measure_to_conditions.items()
            },
            underlying_default_measure,
            cube_name=cube_name,
            measure_metadata=measure_metadata,
        )


FilterCondition = Condition[
    Union[HierarchyIdentifier, LevelIdentifier],
    ConditionComparisonOperatorBound,
    Constant,
    Optional[Literal["and"]],
]


@keyword_only_dataclass
@dataclass(eq=False, frozen=True)
class LevelValueFilteredMeasure(MeasureDescription):
    """A measure on a part of the cube filtered on a level value."""

    _underlying_measure: MeasureDescription
    _condition: FilterCondition

    @override
    def _do_distil(
        self,
        identifier: Optional[MeasureIdentifier] = None,
        /,
        *,
        cube_name: str,
        java_api: JavaApi,
        measure_metadata: Optional[MeasureMetadata] = None,
    ) -> MeasureIdentifier:
        underlying_name: str = self._underlying_measure._distil(
            java_api=java_api, cube_name=cube_name
        ).measure_name

        (
            comparison_conditions,
            isin_conditions,
            hierarchy_isin_conditions,
        ) = decombine_condition(  # type: ignore[var-annotated]
            self._condition,
            allowed_subject_types=(LevelIdentifier,),
            allowed_combination_operators=("and",),
            allowed_target_types=(Constant,),
            allowed_isin_element_types=(Constant,),
        )[0]

        conditions: list[dict[str, object]] = []

        conditions.extend(
            {
                "level": comparison_condition.subject._java_description,
                "type": "constant",
                "operation": comparison_condition.operator,
                "value": to_java_object(
                    comparison_condition.target.value, gateway=java_api.gateway
                ),
            }
            for comparison_condition in comparison_conditions
        )

        conditions.extend(
            {
                "level": isin_condition.subject._java_description,
                "type": "constant",
                "operation": "li",
                "value": to_java_list(
                    [element.value for element in isin_condition.elements],
                    gateway=java_api.gateway,
                ),
            }
            for isin_condition in isin_conditions
        )

        conditions.extend(
            {
                "level": LevelIdentifier(
                    hierarchy_isin_condition.subject,
                    hierarchy_isin_condition.level_names[0],
                )._java_description,
                "type": "constant",
                "operation": "hi",
                "value": [
                    {
                        LevelIdentifier(
                            hierarchy_isin_condition.subject,
                            level_name,
                        )._java_description: member.value
                        for level_name, member in zip(
                            hierarchy_isin_condition.level_names, member_path
                        )
                    }
                    for member_path in hierarchy_isin_condition.member_paths
                ],
            }
            for hierarchy_isin_condition in hierarchy_isin_conditions
        )

        # Create the filtered measure and return its name.
        return java_api.create_measure(
            identifier,
            "FILTER",
            underlying_name,
            conditions,
            cube_name=cube_name,
            measure_metadata=measure_metadata,
        )
