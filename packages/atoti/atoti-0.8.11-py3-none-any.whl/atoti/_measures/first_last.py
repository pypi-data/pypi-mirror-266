from dataclasses import dataclass
from typing import Literal, Optional

from atoti_core import LevelIdentifier, MeasureIdentifier, keyword_only_dataclass
from typing_extensions import override

from .._java_api import JavaApi
from .._measure_description import MeasureDescription
from .._measure_metadata import MeasureMetadata
from .utils import get_measure_name


@keyword_only_dataclass
@dataclass(eq=False, frozen=True)
class FirstLast(MeasureDescription):
    """Shift the value."""

    _underlying_measure: MeasureDescription
    _level_identifier: LevelIdentifier
    _mode: Literal["FIRST", "LAST"]
    _partitioning: Optional[LevelIdentifier]

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
        underlying_name = get_measure_name(
            java_api=java_api, measure=self._underlying_measure, cube_name=cube_name
        )
        return java_api.create_measure(
            identifier,
            "FIRST_LAST",
            underlying_name,
            self._level_identifier._java_description,
            self._mode,
            self._partitioning._java_description
            if self._partitioning is not None
            else None,
            cube_name=cube_name,
            measure_metadata=measure_metadata,
        )
