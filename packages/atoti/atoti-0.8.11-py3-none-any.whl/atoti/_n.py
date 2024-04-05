from typing import Annotated

from pydantic import Field

N = Annotated[int, Field(ge=1)]
