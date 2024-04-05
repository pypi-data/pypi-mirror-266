from pathlib import Path
from typing import Optional

from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class ClientCertificateConfig:
    """The JKS truststore config to enable client certificate authentication (also called mutual TLS or mTLS) on the application.

    This requires :class:`atoti.HttpsConfig` to be configured.

    It can be used alongside the other authentication providers.
    If a user presents valid certificates they will be authenticated, if not they will have to authenticate using the other configured security provider.

    Opening a query session on a session protected with this config can be done using :class:`atoti_query.ClientCertificate`.

    Example:
        >>> from pathlib import Path
        >>> client_certificate = tt.ClientCertificateConfig(
        ...     trust_store=Path("truststore.jks"), trust_store_password="secret"
        ... )
        >>> https = tt.HttpsConfig(certificate=Path("cert.p12"), password="secret")

    """

    trust_store: Path
    """Path to the truststore file generated with the certificate used to sign client certificates."""

    trust_store_password: Optional[str]
    """Password protecting the truststore."""

    username_regex: str = "CN=(.*?)(?:,|$)"
    """Regex to extract the username from the certificate."""
