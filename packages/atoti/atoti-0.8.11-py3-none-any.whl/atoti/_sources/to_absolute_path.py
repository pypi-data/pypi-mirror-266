from pathlib import Path
from typing import Union

from .._path_utils import is_cloud_path


def to_absolute_path(path: Union[Path, str], /) -> str:
    return (
        path
        if isinstance(path, str) and is_cloud_path(path)
        else str(Path(path).absolute())
    )
