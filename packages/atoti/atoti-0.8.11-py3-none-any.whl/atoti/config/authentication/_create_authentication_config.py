from __future__ import annotations

from typing import Union

from ._authentication_config import AuthenticationConfig
from .basic_authentication_config import BasicAuthenticationConfig
from .kerberos_config import KerberosConfig
from .ldap_config import LdapConfig
from .oidc_config import OidcConfig


def create_authentication_config(
    authentication: Union[
        BasicAuthenticationConfig, KerberosConfig, LdapConfig, OidcConfig
    ],
) -> AuthenticationConfig:
    if isinstance(authentication, LdapConfig):
        return AuthenticationConfig(ldap=authentication)
    if isinstance(authentication, KerberosConfig):
        return AuthenticationConfig(kerberos=authentication)
    if isinstance(authentication, BasicAuthenticationConfig):
        return AuthenticationConfig(basic=authentication)
    return AuthenticationConfig(oidc=authentication)
