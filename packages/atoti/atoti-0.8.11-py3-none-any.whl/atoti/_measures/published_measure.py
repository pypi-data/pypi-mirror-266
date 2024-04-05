from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from atoti_core import MeasureIdentifier
from typing_extensions import override

from .._java_api import JavaApi
from .._measure_description import MeasureDescription
from .._measure_metadata import MeasureMetadata


@dataclass(eq=False, frozen=True)
class PublishedMeasure(MeasureDescription):  # pylint: disable=keyword-only-dataclass
    _name: str

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
        raise RuntimeError("Cannot create a measure that already exists in the cube.")
