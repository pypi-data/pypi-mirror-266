from __future__ import annotations

from dataclasses import field
from functools import cache
from uuid import uuid4

from atoti_core import PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass


@cache
def _get_process_id() -> str:
    return str(uuid4())


@keyword_only_dataclass
@dataclass(config=PYDANTIC_CONFIG, frozen=True)
class Event:
    process_id: str = field(default_factory=_get_process_id, init=False)
    event_type: str
