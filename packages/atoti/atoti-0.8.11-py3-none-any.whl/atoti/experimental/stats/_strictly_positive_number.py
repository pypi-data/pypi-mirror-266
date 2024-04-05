from typing import Annotated, Union

from pydantic import Field

StrictlyPositiveNumber = Annotated[Union[int, float], Field(gt=0)]
