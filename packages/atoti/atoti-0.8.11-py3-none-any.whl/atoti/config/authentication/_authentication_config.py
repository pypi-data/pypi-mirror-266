from __future__ import annotations

from typing import Optional

from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass

from .basic_authentication_config import BasicAuthenticationConfig
from .kerberos_config import KerberosConfig
from .ldap_config import LdapConfig
from .oidc_config import OidcConfig


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class AuthenticationConfig:
    """The configuration of the authentication mechanism used by the server to know which users are allowed to connect to the application and which roles they are granted.

    Note:
       This feature is not part of the community edition: it needs to be `unlocked <../../how_tos/unlock_all_features.html>`__.

    If any non-:class:`basic <atoti.BasicAuthenticationConfig>` authentication is configured, basic authentication will be automatically enabled as well to make it easier to create service/technical users.

    Roles and restrictions can be configured using :attr:`~atoti.Session.security`.
    """

    basic: Optional[BasicAuthenticationConfig] = None
    kerberos: Optional[KerberosConfig] = None
    ldap: Optional[LdapConfig] = None
    oidc: Optional[OidcConfig] = None

    def __post_init__(self) -> None:
        assert (
            len([value for value in self.__dict__.values() if value is not None]) == 1
        ), "One and only one authentication mechanism can be configured."
