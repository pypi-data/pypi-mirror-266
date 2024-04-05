from collections.abc import Mapping
from typing import Optional

from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class HttpRequest:
    """Info of an HTTP request."""

    url: str
    """URL on which the client request was made."""

    path_parameters: Mapping[str, str]
    """Mapping from the name of the path parameters to their value for this request."""

    body: Optional[object]
    """Parsed JSON body of the request."""
