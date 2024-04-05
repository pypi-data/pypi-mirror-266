from __future__ import annotations

from collections.abc import Collection, Sequence
from dataclasses import dataclass
from typing import Optional, Union

from atoti_core import LevelIdentifier, MeasureIdentifier, keyword_only_dataclass
from typing_extensions import override

from .._java_api import JavaApi
from .._measure_convertible import NonConstantMeasureConvertible
from .._measure_description import MeasureDescription
from .._measure_metadata import MeasureMetadata
from .utils import convert_measure_args

_Operand = Union[MeasureDescription, str]


@dataclass(frozen=True)
class Operator:  # pylint: disable=keyword-only-dataclass
    """An operator to create a calculated measure from other measures."""

    _name: str
    _operands: Sequence[_Operand]


@dataclass(eq=False, frozen=True)
class CalculatedMeasure(MeasureDescription):  # pylint: disable=keyword-only-dataclass
    """A calculated measure is the result of an operation between other measures."""

    _operator: Operator

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
        return java_api.create_measure(
            identifier,
            "CALCULATED",
            self._operator._name,
            convert_measure_args(
                java_api=java_api,
                cube_name=cube_name,
                args=self._operator._operands,
            ),
            cube_name=cube_name,
            measure_metadata=measure_metadata,
        )


@keyword_only_dataclass
@dataclass(eq=False, frozen=True)
class AggregatedMeasure(MeasureDescription):
    """Aggregated measure."""

    _underlying_measure: NonConstantMeasureConvertible
    _plugin_key: str
    _on_levels: Collection[LevelIdentifier] = ()

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
        return java_api.create_measure(
            identifier,
            "LEAF_AGGREGATION",
            *convert_measure_args(
                java_api=java_api, cube_name=cube_name, args=(self._underlying_measure,)
            ),
            [
                level_identifier._java_description
                for level_identifier in self._on_levels
            ],
            self._plugin_key,
            cube_name=cube_name,
            measure_metadata=measure_metadata,
        )
