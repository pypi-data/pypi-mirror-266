from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class KeyPair:
    public_key: str
    """The public key."""

    private_key: str
    """The private key."""
