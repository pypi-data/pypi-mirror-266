from collections.abc import Mapping
from pathlib import Path
from typing import Literal, Optional, Union

from atoti_core import Plugin

from ._path_utils import is_cloud_path, to_posix_path


def _validate_path(path: Union[Path, str]) -> Union[Path, str]:
    if "*" in str(path):
        raise ValueError("The path could not be parsed correctly.")
    return path


def split_path_and_pattern(
    path: Union[Path, str],
    /,
    extension: Literal[".csv", ".parquet"],
    *,
    plugins: Mapping[str, Plugin],
) -> tuple[Union[Path, str], Optional[str]]:
    """Extract the glob pattern from the path if there is one."""
    # Start by searching for glob characters in the string
    path = to_posix_path(path, plugins=plugins)

    star_index = path.find("*")
    question_index = path.find("?")
    bracket_index = path.find("[") if path.find("]") > -1 else -1
    curly_index = path.find("{") if path.find("}") > -1 else -1

    first_index = min(
        i
        for i in [len(path) + 1, star_index, question_index, bracket_index, curly_index]
        if i > 0
    )

    if first_index == len(path) + 1:
        if path.endswith(extension) or (
            (extension == ".csv") and (path.endswith((".zip", ".tar.gz", ".gz")))
        ):
            return path, None
        # Directories containing multiple partitioned Parquet files are supported.
        if extension == ".parquet":
            return path, "glob:*.parquet"
        raise ValueError(
            "Paths pointing to a directory are not supported, use a glob pattern instead."
        )

    # Search for the first / in the path before the beginning of the glob expression
    separators = [i for i, char in enumerate(path) if char == "/"]
    index = 0
    for i in sorted(separators):
        if i > first_index:
            break
        index = i
    return (
        _validate_path(Path(path[:index]) if not is_cloud_path(path) else path[:index]),
        _validate_glob_pattern(path[index:]),
    )


def _validate_glob_pattern(pattern: str) -> str:
    """Check the pattern meets our requirements and modify it if necessary."""
    if ":" in pattern:
        split = pattern.split(":")
        if split[0] != "glob":
            raise ValueError("Only glob patterns are supported.")
        if split[1][0] == "/":
            # glob pattern doesn't need leading /
            split[1] = split[1][1:]
        return ":".join(split)

    if pattern[0] == "/":
        # glob pattern doesn't need leading /
        pattern = pattern[1:]

    return f"glob:{pattern}"
