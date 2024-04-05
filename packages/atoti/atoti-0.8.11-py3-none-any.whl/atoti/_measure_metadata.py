from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Optional, Union

from atoti_core import keyword_only_dataclass


@keyword_only_dataclass
@dataclass(frozen=True)
class MeasureMetadata:
    description: Optional[str] = None
    folder: Optional[str] = None
    formatter: Optional[str] = None
    visible: Optional[bool] = None

    @property
    def defined_properties(
        self,
    ) -> Mapping[str, Optional[Union[str, bool]]]:
        return asdict(
            self,
            dict_factory=lambda items: {
                key: str(value) for key, value in items if value is not None
            },
        )
