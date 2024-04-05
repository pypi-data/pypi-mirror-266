import os
from collections.abc import Mapping
from pathlib import Path
from typing import Union

from atoti_core import MissingPluginError, Plugin

S3_IDENTIFIER = "s3://"
AZURE_BLOB_IDENTIFIER = ".blob.core.windows.net/"
GCP_IDENTIFIER = "gs://"


def is_cloud_path(path: str) -> bool:
    """Check whether a path is a supported cloud path or not."""
    return path.startswith((S3_IDENTIFIER, GCP_IDENTIFIER)) or (
        AZURE_BLOB_IDENTIFIER in path
    )


def get_atoti_home() -> Path:
    """Get the path from $ATOTI_HOME env variable. If not defined, use $HOME/.atoti."""
    return Path(os.environ.get("ATOTI_HOME", Path.home() / ".atoti"))


def stem_path(path: Union[Path, str]) -> str:
    """Return the final path component, without its suffix."""
    if isinstance(path, Path):
        return path.stem

    if is_cloud_path(path):
        return stem_path(Path(path[path.rfind("/") + 1 :]))
    return stem_path(Path(path))


def to_posix_path(path: Union[Path, str], *, plugins: Mapping[str, Plugin]) -> str:
    if isinstance(path, Path):
        return str(path.as_posix())

    if path.startswith(S3_IDENTIFIER):
        if "aws" not in plugins:
            raise MissingPluginError("aws")
        return path
    if AZURE_BLOB_IDENTIFIER in path:
        if "azure" not in plugins:
            raise MissingPluginError("azure")
        return path
    if path.startswith(GCP_IDENTIFIER):
        if "gcp" not in plugins:
            raise MissingPluginError("gcp")
        return path

    # Do not resolve the path yet as it can contain a glob pattern that pathlib._WindowsFlavour does not support.
    # See also: https://github.com/python/cpython/pull/17
    return str(Path(path).as_posix())


def get_h2_url(path: Path, /) -> str:
    return f"jdbc:h2:file:{path.absolute() / 'content'}"
