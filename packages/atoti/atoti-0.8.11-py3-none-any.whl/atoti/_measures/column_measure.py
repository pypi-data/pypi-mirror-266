from dataclasses import dataclass
from typing import Optional

from atoti_core import ColumnIdentifier, MeasureIdentifier, keyword_only_dataclass
from typing_extensions import override

from .._java_api import JavaApi
from .._measure_description import MeasureDescription
from .._measure_metadata import MeasureMetadata


@keyword_only_dataclass
@dataclass(eq=False, frozen=True)
class ColumnMeasure(MeasureDescription):
    """Measure based on the column of a table."""

    _column_identifier: ColumnIdentifier
    _plugin_key: str

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
        return java_api.aggregated_measure(
            identifier,
            self._plugin_key,
            column_identifier=self._column_identifier,
            cube_name=cube_name,
            measure_metadata=measure_metadata,
        )
