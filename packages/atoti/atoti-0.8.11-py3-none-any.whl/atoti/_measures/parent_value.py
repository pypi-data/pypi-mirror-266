from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Optional, Union

from atoti_core import HierarchyIdentifier, MeasureIdentifier, keyword_only_dataclass
from typing_extensions import override

from .._java_api import JavaApi
from .._measure_convertible import MeasureConvertible
from .._measure_description import MeasureDescription
from .._measure_metadata import MeasureMetadata
from .._measures.utils import get_measure_name


@keyword_only_dataclass
@dataclass(eq=False, frozen=True)
class ParentValue(MeasureDescription):
    """The value of the measure for the parent."""

    _underlying_measure: Union[MeasureDescription, str]
    _degrees: Mapping[HierarchyIdentifier, int]
    _total_value: Optional[MeasureConvertible]
    _apply_filters: bool
    _dense: bool

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
        underlying_name = (
            self._underlying_measure
            if isinstance(self._underlying_measure, str)
            else get_measure_name(
                java_api=java_api, measure=self._underlying_measure, cube_name=cube_name
            )
        )
        total_measure_name: Optional[str] = (
            self._total_value._distil(
                java_api=java_api, cube_name=cube_name
            ).measure_name
            if isinstance(self._total_value, MeasureDescription)
            else None
        )
        total_literal = self._total_value if total_measure_name is None else None

        return java_api.create_measure(
            identifier,
            "PARENT_VALUE",
            underlying_name,
            {
                identifier._java_description: degree
                for identifier, degree in self._degrees.items()
            },
            total_measure_name,
            total_literal,
            self._apply_filters,
            self._dense,
            cube_name=cube_name,
            measure_metadata=measure_metadata,
        )
