from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from atoti_core import Constant, MeasureIdentifier, keyword_only_dataclass
from typing_extensions import override

from .._java_api import JavaApi
from .._measure_description import MeasureDescription
from .._measure_metadata import MeasureMetadata
from .._py4j_utils import to_java_object


@keyword_only_dataclass
@dataclass(eq=False, frozen=True)
class ConstantMeasure(MeasureDescription):
    """A measure equal to a constant."""

    _value: Constant

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
        value = to_java_object(self._value.value, gateway=java_api.gateway)
        return java_api.create_measure(
            identifier,
            "CONSTANT",
            value,
            cube_name=cube_name,
            measure_metadata=measure_metadata,
        )
