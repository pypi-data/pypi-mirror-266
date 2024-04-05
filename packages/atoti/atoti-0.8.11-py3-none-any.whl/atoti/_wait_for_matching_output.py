from __future__ import annotations

import re
import shlex
from datetime import timedelta
from io import StringIO
from subprocess import Popen
from time import monotonic

_DEFAULT_TIMEOUT = timedelta(seconds=100)


def wait_for_matching_output(
    pattern: str,
    *,
    process: Popen[str],
    timeout: timedelta = _DEFAULT_TIMEOUT,
) -> tuple[re.Match[str], str]:
    if process.stdout is None:
        raise ValueError("Expected process to have an stdout.")

    with StringIO() as output:

        def get_error_message(*, reason: str) -> str:
            command = shlex.join(process.args)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
            return "\n".join(
                [
                    reason,
                    "COMMAND:",
                    command,
                    "PATTERN:",
                    pattern,
                    "OUTPUT:",
                    "".join(output.getvalue()),
                ]
            )

        start = monotonic()

        while process.poll() is None:
            if monotonic() > start + timeout.total_seconds():
                if not process.stdout.closed:
                    process.stdout.close()
                raise RuntimeError(
                    get_error_message(
                        reason=f"{timeout.total_seconds()} seconds elapsed but the process output did not match the expected pattern."
                    )
                )

            line = process.stdout.readline()
            output.write(line)

            match = re.search(pattern, line)
            if match:
                return match, output.getvalue()

        if not process.stdout.closed:
            process.stdout.close()
        raise RuntimeError(
            get_error_message(
                reason="Process exited before its output matched the expected pattern."
            )
        )
