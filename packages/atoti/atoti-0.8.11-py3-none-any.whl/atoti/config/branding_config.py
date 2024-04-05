from pathlib import Path
from typing import Annotated, Callable, Optional

from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic import AfterValidator, Field
from pydantic.dataclasses import dataclass


def _create_suffix_checker(
    expected_suffix: str,
    /,
) -> Callable[[Path], Path]:
    def _check_suffix(path: Path, /) -> Path:
        suffix = Path(path).suffix

        if suffix != expected_suffix:
            raise ValueError(
                f"Expected a {expected_suffix} file but got a {suffix} file."
            )

        return path

    return _check_suffix


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class BrandingConfig:
    """The UI elements to `customize the app <../../how_tos/customize_the_app.html>`__ by replacing the Atoti branding with another one (also called white-labeling).

    Note:
        This feature is not part of the community edition: it needs to be `unlocked <../../how_tos/unlock_all_features.html>`__.

    When defined, the :guilabel:`By ActiveViam` signature at the bottom right corner of the app will be removed.

    Example:
        >>> from pathlib import Path
        >>> config = tt.BrandingConfig(
        ...     favicon=Path("favicon.ico"),
        ...     logo=Path("logo.svg"),
        ...     title="Custom title",
        ... )

    """

    favicon: Optional[
        Annotated[Path, AfterValidator(_create_suffix_checker(".ico"))]
    ] = None
    """The file path to a ``.ico`` image that will be used as the favicon."""

    logo: Optional[Annotated[Path, AfterValidator(_create_suffix_checker(".svg"))]] = (
        None
    )
    """The file path to a 20px high ``.svg`` image that will be displayed in the upper-left corner."""

    dark_theme_logo: Optional[
        Annotated[Path, AfterValidator(_create_suffix_checker(".svg"))]
    ] = None
    """The logo displayed in dark theme.

    If ``None``, :attr:`logo` will be used as a fallback (if it is not ``None`` itself).
    """

    title: Annotated[
        str,
        Field(
            exclude=True  # Not sent to the server since it is handled client side.
        ),
    ] = "Atoti"
    """The title to give to the browser tab (in the home page)."""
