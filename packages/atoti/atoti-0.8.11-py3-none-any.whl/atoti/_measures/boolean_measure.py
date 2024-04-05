from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from atoti_core import MeasureIdentifier
from typing_extensions import override

from .._java_api import JavaApi
from .._measure_description import MeasureDescription
from .._measure_metadata import MeasureMetadata
from .utils import convert_measure_args


@dataclass(eq=False, frozen=True)
class BooleanMeasure(MeasureDescription):  # pylint: disable=keyword-only-dataclass
    """Boolean operation between measures."""

    _operator: str
    _operands: tuple[MeasureDescription, ...]

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
            "BOOLEAN",
            self._operator,
            convert_measure_args(
                java_api=java_api, cube_name=cube_name, args=self._operands
            ),
            cube_name=cube_name,
            measure_metadata=measure_metadata,
        )
