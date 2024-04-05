from dataclasses import dataclass
from typing import Optional

from atoti_core import HierarchyIdentifier, MeasureIdentifier, keyword_only_dataclass
from typing_extensions import override

from ..._java_api import JavaApi
from ..._measure_description import MeasureDescription
from ..._measure_metadata import MeasureMetadata


@keyword_only_dataclass
@dataclass(eq=False, frozen=True)
class IrrMeasure(MeasureDescription):
    """Internal Rate of Return measure."""

    _cash_flows_measure: MeasureDescription
    _market_value_measure: MeasureDescription
    _date_hierarchy_identifier: HierarchyIdentifier
    _precision: float

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
        # Distil the underlying measures
        cash_flows_name: str = self._cash_flows_measure._distil(
            java_api=java_api, cube_name=cube_name
        ).measure_name
        market_value_name: str = self._market_value_measure._distil(
            java_api=java_api, cube_name=cube_name
        ).measure_name

        return java_api.create_measure(
            identifier,
            "IRR",
            market_value_name,  # market value first
            cash_flows_name,
            self._date_hierarchy_identifier._java_description,
            self._precision,
            cube_name=cube_name,
            measure_metadata=measure_metadata,
        )
