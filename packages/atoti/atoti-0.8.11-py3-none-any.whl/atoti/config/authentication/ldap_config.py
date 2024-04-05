from typing import Optional

from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class LdapConfig:
    """The configuration to connect to an `LDAP <https://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol>`__ authentication provider.

    The user's roles can be defined using :attr:`atoti_query.security.Security.ldap` and :attr:`~atoti_query.security.Security.individual_roles`.

    Example:
        >>> auth_config = tt.LdapConfig(
        ...     url="ldap://example.com:389",
        ...     base_dn="dc=example,dc=com",
        ...     user_search_base="ou=people",
        ...     group_search_base="ou=roles",
        ... )
    """

    url: str
    """The LDAP URL including the protocol and port."""

    base_dn: str
    """The Base Distinguished Name of the directory service."""

    manager_dn: Optional[str] = None
    """The Distinguished Name (DN) used to log into the Directory Service and to search for user accounts.

    If ``None``, the connection to the service will be done anonymously."""

    manager_password: Optional[str] = None
    """The password for the manager account specified in the *manager_dn* attribute."""

    user_search_filter: str = "(uid={0})"
    """The LDAP filter used to search for users.

    The substituted parameter is the user's login name.
    """

    user_search_base: str = ""
    """Search base for user searches."""

    group_search_filter: str = "(uniqueMember={0})"
    """The LDAP filter to search for groups.

    The substituted parameter is the DN of the user.
    """

    group_search_base: Optional[str] = None
    """The search base for group membership searches."""

    group_role_attribute_name: str = "cn"
    """The attribute name that maps a group to a role."""
