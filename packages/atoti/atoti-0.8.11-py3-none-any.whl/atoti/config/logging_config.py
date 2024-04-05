from io import TextIOBase
from pathlib import Path
from typing import Annotated, Optional, TextIO, Union

from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic import PlainSerializer
from pydantic.dataclasses import dataclass


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class LoggingConfig:
    """The configuration describing how the session logs will be handled.

    Example:
        >>> logging_config = tt.LoggingConfig(destination="./atoti/server.log")

    """

    destination: Optional[
        Annotated[
            Union[Path, TextIO, TextIOBase],
            PlainSerializer(
                lambda destination: None  # The io configured to write the logs to is not serializable and Java does not need it.
                if isinstance(destination, TextIOBase)
                else destination
            ),
        ]
    ] = None
    """The place where the session logs will be written to.

    If ``None``, the logs will be written to ``logs/server.log`` in the session directory under ``$ATOTI_HOME`` (this environment variable itself defaults to ``$HOME/.atoti``).

    Note:
        Unless an instance of :class:`io.TextIOBase` is passed, the rolling policy is:

        * Maximum file size of 10MB.
        * Maximum history of 7 days.

        Once the maximum size is reached, logs are archived following the pattern ``f"{destination}.{date}.{i}.gz"`` where ``date`` is the creation date of the file in the ``yyyy-MM-dd`` format and ``i`` an integer incremented during the day.

    Example:

        To stream the session logs to the Python process' standard output:

        >>> import sys
        >>> logging_config = tt.LoggingConfig(destination=sys.stdout)
    """

    @property
    def _destination_io(self) -> Optional[TextIOBase]:
        return (
            self.destination
            if self.destination and isinstance(self.destination, TextIOBase)
            else None
        )
