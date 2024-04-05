from pathlib import Path
from typing import Annotated, Optional

from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic import Field
from pydantic.dataclasses import dataclass


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class HttpsConfig:
    """The PKCS 12 keystore configuration to enable HTTPS on the application.

    Note:
        This feature is not part of the community edition: it needs to be `unlocked <../../how_tos/unlock_all_features.html>`__.

    Note:
        PEM or DER certificates can be `converted to PKCS 12 with OpenSSL <https://stackoverflow.com/questions/56241667/convert-certificate-in-der-or-pem-to-pkcs12/56244685#56244685>`__.

    Example:
        >>> from pathlib import Path
        >>> https_config = tt.HttpsConfig(certificate=Path("cert.p12"), password="secret")

    """

    certificate: Path
    """The path to the certificate."""

    password: str
    """The password to read the certificate."""

    domain: Annotated[str, Field(exclude=True)] = "localhost"
    """The domain certified by the certificate."""

    certificate_authority: Annotated[Optional[Path], Field(exclude=True)] = None
    """Path to the custom certificate authority to use to verify the HTTPS connection.

    Required when *certificate* is not signed by some trusted public certificate authority.
    """
