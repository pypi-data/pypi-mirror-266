from collections.abc import Mapping
from dataclasses import dataclass
from typing import Optional

from atoti_core import (
    ConstantValue,
    LevelIdentifier,
    MeasureIdentifier,
    keyword_only_dataclass,
)
from typing_extensions import override

from .._java_api import JavaApi
from .._measure_description import MeasureDescription
from .._measure_metadata import MeasureMetadata
from .._py4j_utils import to_java_map, to_java_object


@keyword_only_dataclass
@dataclass(repr=True, frozen=True)
class SwitchOnMeasure(MeasureDescription):
    """A measure that switches between different measures based on the value of a level."""

    _subject: LevelIdentifier
    _cases: Mapping[
        ConstantValue,
        MeasureDescription,
    ]
    _default: MeasureDescription
    _above_level: Optional[MeasureDescription] = None

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
        return java_api.create_measure(
            identifier,
            "SWITCH_ON",
            java_api.gateway.jvm.com.activeviam.copper.LevelIdentifier.fromDescription(  # pyright: ignore[reportCallIssue,reportAttributeAccessIssue,reportOptionalCall,reportOptionalMemberAccess]
                self._subject._java_description
            ),
            to_java_map(
                {
                    to_java_object(key, gateway=java_api.gateway): value._distil(
                        java_api=java_api, cube_name=cube_name
                    ).measure_name
                    for key, value in self._cases.items()
                },
                gateway=java_api.gateway,
            ),
            self._default._distil(java_api=java_api, cube_name=cube_name).measure_name,
            None
            if self._above_level is None
            else self._above_level._distil(
                java_api=java_api, cube_name=cube_name
            ).measure_name,
            cube_name=cube_name,
            measure_metadata=measure_metadata,
        )
