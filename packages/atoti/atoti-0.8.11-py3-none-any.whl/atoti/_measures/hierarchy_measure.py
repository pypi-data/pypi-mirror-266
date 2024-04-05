from dataclasses import dataclass
from typing import Optional

from atoti_core import HierarchyIdentifier, MeasureIdentifier
from typing_extensions import override

from .._java_api import JavaApi
from .._measure_description import MeasureDescription
from .._measure_metadata import MeasureMetadata


@dataclass(eq=False, frozen=True)
class HierarchyMeasure(MeasureDescription):  # pylint: disable=keyword-only-dataclass
    _hierarchy_identifier: HierarchyIdentifier

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
            "HIERARCHY",
            self._hierarchy_identifier._java_description,
            cube_name=cube_name,
            measure_metadata=measure_metadata,
        )
