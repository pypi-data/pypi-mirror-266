from typing import Annotated, Optional

from atoti_core import (
    PYDANTIC_CONFIG as _PYDANTIC_CONFIG,
    FrozenMapping,
    MissingPluginError,
    frozendict,
    keyword_only_dataclass,
)
from pydantic import AfterValidator
from pydantic.dataclasses import dataclass

from .._jdbc_utils import normalize_jdbc_url


def _infer_driver(url: str, /) -> str:
    try:
        from atoti_sql._infer_driver import (  # pylint: disable=submodule-import, nested-import, undeclared-dependency
            infer_driver,
        )
    except ImportError as error:
        raise MissingPluginError("sql") from error

    return infer_driver(url)


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class UserContentStorageConfig:
    """The advanced configuration for the user content storage.

    Note:
        JDBC backed user content storage requires the :mod:`atoti-sql <atoti_sql>` plugin.

    Example:
        >>> user_content_storage_config = tt.UserContentStorageConfig(
        ...     url="mysql://localhost:7777/example?user=username&password=passwd"
        ... )


        For drivers not embedded with :mod:`atoti-sql <atoti_sql>`, extra JARs can be passed:

        >>> import glob
        >>> user_content_storage = tt.UserContentStorageConfig(
        ...     url="jdbc:bigquery://https://www.googleapis.com/bigquery/v2:443;ProjectId=PROJECT_ID;OAuthType=0;OAuthServiceAcctEmail=EMAIL_OF_SERVICEACCOUNT;OAuthPvtKeyPath=path/to/json/keys;",
        ...     driver="com.simba.googlebigquery.jdbc42.Driver",
        ... )
        >>> extra_jars = glob.glob("./odbc_jdbc_drivers/*.jar")

    """

    url: Annotated[str, AfterValidator(normalize_jdbc_url)]
    """The JDBC connection URL of the database.

    The ``jdbc:`` prefix is optional but the database specific part (such as ``h2:`` or ``mysql:``) is mandatory.
    For instance:

    * ``h2:file:/home/user/database/file/path;USER=username;PASSWORD=passwd``
    * ``mysql://localhost:7777/example?user=username&password=passwd``
    * ``postgresql://postgresql.db.server:5430/example?user=username&password=passwd``

    More examples can be found `here <https://www.baeldung.com/java-jdbc-url-format>`__.

    This defines Hibernate's `URL <https://javadoc.io/static/org.hibernate/hibernate-core/5.6.15.Final/org/hibernate/cfg/AvailableSettings.html#URL>`__ option.
    """

    driver: Optional[str] = None
    """The JDBC driver used to load the data.

    If ``None``, the driver is inferred from the URL.
    Drivers can be found in the :mod:`atoti_sql.drivers` module.

    This defines Hibernate's `DRIVER <https://javadoc.io/static/org.hibernate/hibernate-core/5.6.15.Final/org/hibernate/cfg/AvailableSettings.html#DRIVER>`__ option.
    """

    hibernate_options: FrozenMapping[str, str] = frozendict()
    """Extra options to pass to Hibernate.

    See `AvailableSettings <https://javadoc.io/static/org.hibernate/hibernate-core/5.6.15.Final/org/hibernate/cfg/AvailableSettings.html>`__.
    """

    def __post_init__(self) -> None:
        if self.driver is None:
            self.__dict__["driver"] = _infer_driver(self.url)
