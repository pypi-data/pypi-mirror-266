from __future__ import annotations

from pathlib import Path

from atoti_core import TableIdentifier
from typing_extensions import override

from .data_source import DataSource


class ArrowDataSource(DataSource):
    @property
    @override
    def key(self) -> str:
        return "ARROW"

    def load_arrow_into_table(
        self,
        identifier: TableIdentifier,
        path: Path,
        /,
        *,
        scenario_name: str,
    ) -> None:
        self.load_data_into_table(
            identifier,
            {"absolutePath": str(path)},
            scenario_name=scenario_name,
        )
