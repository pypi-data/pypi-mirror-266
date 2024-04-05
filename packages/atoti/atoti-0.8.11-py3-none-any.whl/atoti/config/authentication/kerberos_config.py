from pathlib import Path
from typing import Optional

from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class KerberosConfig:
    """The configuration to connect to a `Kerberos <https://web.mit.edu/kerberos/>`__ authentication provider.

    The user's roles can be defined using :attr:`atoti_query.security.Security.kerberos` and :attr:`~atoti_query.security.Security.individual_roles`.

    Example:
        >>> from pathlib import Path
        >>> auth_config = tt.KerberosConfig(
        ...     service_principal="HTTP/localhost",
        ...     keytab=Path("config") / "example.keytab",
        ...     krb5_config=Path("config") / "example.krb5",
        ... )
    """

    service_principal: str
    """The principal that the Atoti application will use."""

    keytab: Optional[Path] = None
    """The path to the keytab file to use."""

    krb5_config: Optional[Path] = None
    """The path to the Kerberos config file.

    Defaults to the OS-specific default location.
    """
