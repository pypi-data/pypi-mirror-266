import argparse
from pathlib import Path
from shutil import copytree, ignore_patterns
from typing import Final

_TUTORIAL_DIRECTORY = Path(Path(__file__).parent) / "tutorial"


def _copy_tutorial(path: Path) -> None:
    """Copy the tutorial files to the given path."""
    copytree(_TUTORIAL_DIRECTORY, path, ignore=ignore_patterns(".ipynb_checkpoints"))


if __name__ == "__main__":
    parser: Final = argparse.ArgumentParser(description=_copy_tutorial.__doc__)
    parser.add_argument(
        "path",
        help="The path to the directory that will be created and where the tutorial files will be copied to.",
        type=Path,
    )
    args: argparse.Namespace = parser.parse_args()
    _copy_tutorial(args.path)
    print(f"The tutorial files have been copied to {args.path.resolve()}")  # noqa: T201
