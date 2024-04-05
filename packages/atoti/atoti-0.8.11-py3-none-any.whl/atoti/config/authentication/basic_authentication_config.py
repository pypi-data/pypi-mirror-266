from typing import Optional

from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class BasicAuthenticationConfig:
    """The `basic authentication <https://en.wikipedia.org/wiki/Basic_access_authentication>`__ configuration.

    It is the most basic way to set up security since it only requires defining :attr:`~atoti_query.security.basic_security.BasicSecurity.credentials` and :attr:`~atoti_query.security.Security.individual_roles`.

    See Also:
        :class:`atoti_query.BasicAuthentication`.
    """

    realm: Optional[str] = None
    """The realm describing the protected area.

    Different realms can be used to isolate sessions running on the same domain (regardless of the port).
    The realm will also be displayed by the browser when prompting for credentials.
    Defaults to some machine-wide unique ID.

    Example:

        >>> basic_auth_config = tt.BasicAuthenticationConfig(realm="Example")
    """
