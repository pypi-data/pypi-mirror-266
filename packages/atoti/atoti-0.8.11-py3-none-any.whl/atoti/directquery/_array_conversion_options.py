from typing import Optional, Union

from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass

from . import MultiColumnArrayConversion, MultiRowArrayConversion


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class ArrayConversionOptions:
    array_conversion: Optional[
        Union[MultiColumnArrayConversion, MultiRowArrayConversion]
    ] = None
    """Option to convert some values spread over multiple columns or rows into array columns."""
