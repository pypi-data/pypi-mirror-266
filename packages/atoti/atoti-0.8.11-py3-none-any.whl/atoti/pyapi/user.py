from atoti_core import (
    PYDANTIC_CONFIG as _PYDANTIC_CONFIG,
    FrozenSequence,
    keyword_only_dataclass,
)
from pydantic.dataclasses import dataclass


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class User:
    """Info of a user calling a custom HTTP endpoint."""

    name: str
    """Name of the user calling the endpoint."""

    roles: FrozenSequence[str]
    """Roles of the user calling the endpoint."""
