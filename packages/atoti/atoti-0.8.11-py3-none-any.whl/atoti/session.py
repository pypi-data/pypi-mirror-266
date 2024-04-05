from __future__ import annotations

import tempfile
from collections.abc import (
    Mapping,
    MutableMapping,
    Sequence,
    Set as AbstractSet,
)
from datetime import datetime, timedelta
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Optional,
    Union,
    cast,
)
from warnings import warn

import pandas as pd
import pyarrow as pa
from atoti_core import (
    BASE_SCENARIO_NAME as _BASE_SCENARIO_NAME,
    PYDANTIC_CONFIG as _PYDANTIC_CONFIG,
    ColumnIdentifier,
    Condition,
    ConditionCombinationOperatorBound,
    ConditionComparisonOperatorBound,
    Constant,
    ConstantValue,
    DataType,
    FrozenMapping,
    Plugin,
    SequenceOrDeprecatedSet,
    TableIdentifier,
    doc,
    frozendict,
    keyword_only_dataclass,
)
from numpy.typing import NDArray
from pydantic.dataclasses import dataclass
from typing_extensions import override

from ._arrow_utils import get_data_types_from_arrow
from ._docs_utils import (
    CLIENT_SIDE_ENCRYPTION_DOC as _CLIENT_SIDE_ENCRYPTION_DOC,
    CSV_KWARGS as _CSV_KWARGS,
    EXTERNAL_TABLE_KWARGS as _EXTERNAL_TABLE_KWARGS,
    PARQUET_KWARGS as _PARQUET_KWARGS,
    SQL_KWARGS as _SQL_KWARGS,
    TABLE_CREATION_KWARGS as _TABLE_CREATION_KWARGS,
)
from ._file_utils import split_path_and_pattern
from ._local_session import LocalSession
from ._pandas_utils import pandas_to_arrow
from ._path_utils import get_h2_url, stem_path
from ._sources.csv import CsvDataSource, CsvPrivateParameters
from ._sources.parquet import ParquetDataSource
from ._spark_utils import write_spark_to_parquet
from ._transaction import Transaction
from .client_side_encryption_config import ClientSideEncryptionConfig
from .config import (
    BasicAuthenticationConfig,
    BrandingConfig,
    ClientCertificateConfig,
    HttpsConfig,
    I18nConfig,
    JwtConfig,
    KerberosConfig,
    LdapConfig,
    LoggingConfig,
    OidcConfig,
    UserContentStorageConfig,
)
from .config._session_config import SessionConfig
from .config.authentication._create_authentication_config import (
    create_authentication_config,
)
from .cube import Cube
from .cubes import Cubes
from .directquery import MultiColumnArrayConversion
from .directquery._array_conversion_options import ArrayConversionOptions
from .directquery._external_aggregate_table import ExternalAggregateTable
from .directquery._external_aggregate_table._external_aggregate_tables import (
    ExternalAggregateTables,
)
from .directquery._external_database_connection import ExternalDatabaseConnectionT
from .directquery._external_database_connection_info import (
    ExternalDatabaseConnectionInfo,
)
from .directquery._external_table import ExternalTableT_co
from .directquery._external_table_options import ExternalTableOptions
from .table import Table
from .tables import Tables

if TYPE_CHECKING:
    # pyspark is an optional dependency.
    from pyspark.sql import (  # pylint: disable=undeclared-dependency, nested-import
        DataFrame as SparkDataFrame,
    )
else:
    SparkDataFrame = object


_CubeCreationMode = Literal["auto", "manual", "no_measures"]

_DEFAULT_LICENSE_MINIMUM_REMAINING_TIME = timedelta(days=7)


def _infer_table_name(
    *, path: Union[Path, str], pattern: Optional[str], table_name: Optional[str]
) -> str:
    """Infer the name of a table given the path and table_name parameters."""
    if pattern is not None and table_name is None:
        raise ValueError(
            "The table_name parameter is required when the path argument is a glob pattern."
        )
    return table_name or stem_path(path).capitalize()


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class _SessionPrivateParameters:
    address: Optional[str] = None
    config: Optional[Any] = None
    # Enabling authentication by default makes it easy to detect an existing detached process: if an unauthenticated connection can be made on Py4J's default port it means it's a detached process.
    enable_py4j_auth: bool = True
    license_key: Optional[str] = None
    plugins: Optional[FrozenMapping[str, Plugin]] = None
    py4j_server_port: Optional[int] = None
    start_application: bool = True
    wrap_start_error: bool = True


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class _CreateTablePrivateParameters:
    is_parameter_table: bool = False


class Session(LocalSession[Cubes]):
    """The primary entry point for Atoti applications.

    A session is a process holding data in :attr:`~atoti.Session.tables` and aggregating it in :attr:`~atoti.Session.cubes`.
    It also serves a web app for data exploration accessible with :attr:`~link`.
    """

    def __init__(
        self,
        *,
        name: Optional[str] = "Unnamed",
        app_extensions: Mapping[str, Path] = frozendict(),
        authentication: Optional[
            Union[BasicAuthenticationConfig, KerberosConfig, LdapConfig, OidcConfig]
        ] = None,
        branding: Optional[BrandingConfig] = None,
        client_certificate: Optional[ClientCertificateConfig] = None,
        extra_jars: SequenceOrDeprecatedSet[Path] = (),
        https: Optional[HttpsConfig] = None,
        i18n: Optional[I18nConfig] = None,
        java_options: SequenceOrDeprecatedSet[str] = (),
        jwt: Optional[JwtConfig] = None,
        logging: Optional[LoggingConfig] = None,
        port: int = 0,
        ready: bool = True,
        same_site: Optional[Literal["none", "strict"]] = None,
        user_content_storage: Optional[
            Union[
                Path,
                str,
                UserContentStorageConfig,
            ]
        ] = None,
        **kwargs: Any,
    ):
        """Create a session.

        This will start an Atoti Server in a new process.
        If the :guilabel:`JAVA_HOME` environment variable is not defined or if it points to an unsupported Java version, the JVM from `jdk4py <https://github.com/activeviam/jdk4py>`__ will be used instead.

        Args:
            name: The name of the session.

                For a better prototyping experience in notebooks, creating a session with the same name as an already running session will close the older one.
                Pass ``None`` to opt out of this behavior.
            app_extensions: Mapping from the name of an extension (i.e. :guilabel:`name` property in their :guilabel:`package.json`) to the path of its :guilabel:`dist` directory.

                Note:
                    This feature is not part of the community edition: it needs to be `unlocked <../../how_tos/unlock_all_features.html>`__.

                Extensions can `enhance the app <../../how_tos/customize_the_app.html>`__ in many ways such as:

                * Adding new type of widgets.
                * Attaching custom menu items or titlebar buttons to a set of widgets.
                * Providing other React contexts to the components rendered by the app.

                The :download:`app extension template <../app-extension-template/extension.zip>` can be used as a starting point.

                See Also:
                    Available extensions in :mod:`atoti.app_extension`.

            authentication: The configuration to enable authentication on the session.

                Note:
                    This feature is not part of the community edition: it needs to be `unlocked <../../how_tos/unlock_all_features.html>`__.

            branding: The config to customize some elements of the UI to change its appearance.
            client_certificate: The config to enable client certificate based authentication on the session.
            extra_jars: The paths to the JARs to add to the classpath of the Java process when starting the session.
            https: The config providing certificates to enable HTTPS on the session.
            i18n: The config to internationalize the session.
            java_options: The additional options to pass when starting the Java process (e.g. for optimization or debugging purposes).

                In particular, the ``-Xmx`` option can be set to increase the amount of RAM that the session can use.

                If this option is not specified, the JVM default memory setting is used which is 25% of the machine memory.
            jwt: The config to set the key pair used to validate JWTs when authenticating with the session.
            logging: The config describing how to handle session logs.
            port: The port on which the session will be exposed.

                Defaults to a random available port.
            ready: The initial value of :attr:`ready`.
            same_site: The value to use for the *SameSite* attribute of the HTTP cookie sent by the session when *authentication* is configured.

                Note:
                    This feature is not part of the community edition: it needs to be `unlocked <../../how_tos/unlock_all_features.html>`__.

                See https://web.dev/samesite-cookies-explained for more information.

                Setting it to ``none`` requires the session to be served through HTTPS.

                Defaults to ``lax``.
            user_content_storage: The location of the database where the user content will be stored.
                The user content is what is not part of the data sources, such as the dashboards, widgets, and filters saved in the application.
                If a path to a directory is given, it will be created if needed.
                When ``None``, the user content is kept in memory and is thus lost when the session is closed.
        """
        private_parameters = _SessionPrivateParameters(**kwargs)

        if private_parameters.start_application:
            config = private_parameters.config or SessionConfig(
                app_extensions=app_extensions,
                authentication=create_authentication_config(authentication)
                if authentication
                else None,
                branding=branding,
                client_certificate=client_certificate,
                extra_jars=list(extra_jars),
                https=https,
                i18n=i18n,
                java_options=list(java_options),
                jwt=jwt,
                logging=logging,
                port=port,
                ready=ready,
                same_site=same_site,
                user_content_storage=UserContentStorageConfig(
                    url=get_h2_url(Path(user_content_storage)),
                    driver="org.h2.Driver",
                )
                if isinstance(user_content_storage, (Path, str))
                else user_content_storage,
            )

            super().__init__(
                address=private_parameters.address,
                config=config,
                distributed=False,
                enable_py4j_auth=private_parameters.enable_py4j_auth,
                license_key=private_parameters.license_key,
                name=name,
                plugins=private_parameters.plugins,
                py4j_server_port=private_parameters.py4j_server_port,
                start_application=private_parameters.start_application,
                wrap_start_error=private_parameters.wrap_start_error,
            )
        else:
            super().__init__(
                name=name,
                address=private_parameters.address,
                config=SessionConfig(),
                distributed=False,
                enable_py4j_auth=False,
                license_key=private_parameters.license_key,
                plugins=private_parameters.plugins,
                py4j_server_port=private_parameters.py4j_server_port,
                start_application=private_parameters.start_application,
                wrap_start_error=private_parameters.wrap_start_error,
            )

        self._warn_if_license_about_to_expire()

        for plugin in self._plugins.values():
            plugin.post_init_session(self)

    @property
    @override
    def cubes(self) -> Cubes:
        """Cubes of the session."""
        return Cubes(
            delete_cube=self._java_api.delete_cube,
            get_cube=self._get_cube,
            get_cubes=self._get_cubes,
        )

    @property
    def tables(self) -> Tables:
        """Tables of the session."""
        return Tables(
            client=self._client,
            java_api=self._java_api,
            load_kafka=self._load_kafka,
            load_sql=self._load_sql,
            plugins=self._plugins,
        )

    @doc(
        **_TABLE_CREATION_KWARGS,
        keys_argument="""{"Date", "Product"}""",
        types_argument="""{"Date": tt.LOCAL_DATE, "Product": tt.STRING, "Quantity": tt.DOUBLE}""",
    )
    def create_table(
        self,
        name: str,
        *,
        types: Mapping[str, DataType],
        keys: Union[AbstractSet[str], Sequence[str]] = frozenset(),
        partitioning: Optional[str] = None,
        default_values: Mapping[str, Optional[ConstantValue]] = frozendict(),
        **kwargs: Any,
    ) -> Table:
        """Create an empty table with columns of the given *types*.

        Args:
            name: The name of the table.
            types: The table column names and their corresponding :mod:`data type <atoti.type>`.
            {keys}
            {partitioning}
            {default_values}

        Example:
            >>> from datetime import date
            >>> table = session.create_table(
            ...     "Product",
            ...     keys={keys_argument},
            ...     types={types_argument},
            ... )
            >>> table.head()
            Empty DataFrame
            Columns: [Quantity]
            Index: []
            >>> table.append(
            ...     (date(2021, 5, 19), "TV", 15.0),
            ...     (date(2022, 8, 17), "Car", 2.0),
            ... )
            >>> table.head()
                                Quantity
            Date       Product
            2021-05-19 TV           15.0
            2022-08-17 Car           2.0

            Inserting a row with the same key values as an existing row replaces the latter:

            >>> table += (date(2021, 5, 19), "TV", 8.0)
            >>> table.head()
                                Quantity
            Date       Product
            2021-05-19 TV            8.0
            2022-08-17 Car           2.0

        """
        private_parameters = _CreateTablePrivateParameters(**kwargs)
        identifier = TableIdentifier(name)
        self._java_api.create_table(
            identifier,
            types=types,
            keys=[column_name for column_name in types if column_name in keys]
            if isinstance(keys, AbstractSet)
            else keys,
            partitioning=partitioning,
            default_values={
                column_name: None if value is None else Constant(value)
                for column_name, value in default_values.items()
            },
            is_parameter_table=private_parameters.is_parameter_table,
        )
        return Table(
            identifier,
            client=self._client,
            java_api=self._java_api,
            load_kafka=self._load_kafka,
            load_sql=self._load_sql,
            plugins=self._plugins,
        )

    def connect_to_external_database(
        self,
        connection_info: ExternalDatabaseConnectionInfo[
            ExternalDatabaseConnectionT, ExternalTableT_co
        ],
        /,
    ) -> ExternalDatabaseConnectionT:
        """Connect to an external database using DirectQuery.

        Note:
            This feature is not part of the community edition: it needs to be `unlocked <../../how_tos/unlock_all_features.html>`__.

        Args:
            connection_info: Information needed to connect to the external database.
                Each `DirectQuery plugin <../../reference.html#directquery>`__ has its own ``*ConnectionInfo`` class.
        """
        self._java_api.connect_to_database(
            connection_info._database_key,
            url=connection_info._url,
            password=connection_info._password,
            options=connection_info._options,
        )
        return connection_info._get_database_connection(self._java_api)

    @doc(
        **_EXTERNAL_TABLE_KWARGS,
        columns_argument="""{"SALE_ID": "Sale ID", "DATE": "Date", "PRODUCT": "Product", "QUANTITY": "Quantity"}""",
    )
    def add_external_table(
        self,
        external_table: ExternalTableT_co,  # type: ignore[misc] # pyright: ignore[reportGeneralTypeIssues]
        /,
        table_name: Optional[str] = None,
        *,
        columns: Mapping[str, str] = frozendict(),
        options: Optional[ExternalTableOptions[ExternalTableT_co]] = None,
    ) -> Table:
        """Add a table from an external database to the session.

        Args:
            external_table: The external database table from which to build the session table.
                Instances of such tables are obtained through an external database connection.
            table_name: The name to give to the table in the session.
                If ``None``, the name of the external table is used.
            {columns}
            options: The database specific options to read the table.
                Each `DirectQuery plugin <../../reference.html#directquery>`__ has its own ``*TableOptions`` class.

        Example:
            .. doctest:: add_external_table
                :hide:

                >>> import os
                >>> from atoti_directquery_snowflake import SnowflakeConnectionInfo
                >>> connection_info = SnowflakeConnectionInfo(
                ...     "jdbc:snowflake://"
                ...     + os.environ["SNOWFLAKE_ACCOUNT_IDENTIFIER"]
                ...     + ".snowflakecomputing.com/?user="
                ...     + os.environ["SNOWFLAKE_USERNAME"]
                ...     + "&database=TEST_RESOURCES"
                ...     + "&schema=TESTS",
                ...     password=os.environ["SNOWFLAKE_PASSWORD"],
                ... )

            .. doctest:: add_external_table

                >>> from atoti_directquery_snowflake import SnowflakeTableOptions
                >>> external_database = session.connect_to_external_database(connection_info)
                >>> external_table = external_database.tables["TUTORIAL", "SALES"]
                >>> external_table.columns
                ['SALE_ID', 'DATE', 'SHOP', 'PRODUCT', 'QUANTITY', 'UNIT_PRICE']

            Add the external table, filtering out some columns and renaming the remaining ones:

            .. doctest:: add_external_table

                >>> table = session.add_external_table(
                ...     external_table,
                ...     table_name="sales_renamed",
                ...     columns={columns_argument},
                ...     options=SnowflakeTableOptions(keys=["Sale ID"]),
                ... )
                >>> table.head().sort_index()
                              Date Product  Quantity
                Sale ID
                S0007   2022-02-01   BED_2       1.0
                S0008   2022-01-31   BED_2       1.0
                S0009   2022-01-31   BED_2       1.0
                S0010   2022-01-31   BED_2       3.0
                S0019   2022-02-02   HOO_5       1.0

        """
        if table_name is None:
            table_name = external_table._identifier.table_name

        array_conversion = None
        clustering_columns = None
        keys = None

        if options is not None:
            if isinstance(options, ArrayConversionOptions):
                array_conversion = options.array_conversion

            clustering_columns = (
                frozenset(options.clustering_columns)
                if options.clustering_columns
                else None
            )
            keys = tuple(options.keys) if options.keys else None

        if array_conversion is not None:
            if isinstance(array_conversion, MultiColumnArrayConversion):
                self._java_api.add_external_multi_column_array_table(
                    external_table._database_key,
                    column_prefixes=array_conversion.column_prefixes,
                    clustering_columns=clustering_columns
                    if clustering_columns
                    else None,
                    columns=columns,
                    identifier=external_table._identifier,
                    keys=keys,
                    local_table_identifier=TableIdentifier(table_name),
                )
            else:
                self._java_api.add_external_table_with_multi_row_arrays(
                    external_table._database_key,
                    array_columns=array_conversion.array_columns,
                    clustering_columns=clustering_columns,
                    identifier=external_table._identifier,
                    index_column=array_conversion.index_column,
                    local_table_identifier=TableIdentifier(table_name),
                    columns=columns,
                )
        else:
            # Table without conversion
            self._java_api.add_external_table(
                external_table._database_key,
                clustering_columns=clustering_columns,
                columns=columns,
                identifier=external_table._identifier,
                keys=keys,
                local_table_identifier=TableIdentifier(table_name),
            )
        self._java_api.refresh()
        return Table(
            TableIdentifier(table_name),
            client=self._client,
            java_api=self._java_api,
            load_kafka=self._load_kafka,
            load_sql=self._load_sql,
            plugins=self._plugins,
        )

    def _synchronize_with_external_database(self) -> None:
        self._java_api.synchronize_with_external_database()

    @property
    def _external_aggregate_tables(self) -> MutableMapping[str, ExternalAggregateTable]:
        return ExternalAggregateTables(
            java_api=self._java_api,
        )

    @doc(**_TABLE_CREATION_KWARGS, keys_argument="""{"Product"}""")
    def read_pandas(
        self,
        dataframe: pd.DataFrame,
        /,
        *,
        table_name: str,
        keys: Union[AbstractSet[str], Sequence[str]] = frozenset(),
        partitioning: Optional[str] = None,
        types: Mapping[str, DataType] = frozendict(),
        default_values: Mapping[str, Optional[ConstantValue]] = frozendict(),
        **kwargs: Any,
    ) -> Table:
        """Read a pandas DataFrame into a table.

        All the named indices of the DataFrame are included into the table.
        Multilevel columns are flattened into a single string name.

        Args:
            dataframe: The DataFrame to load.
            {table_name}
            {keys}
            {partitioning}
            types: Types for some or all columns of the table.
                Types for non specified columns will be inferred from pandas dtypes.
            {default_values}

        Example:
            >>> dataframe = pd.DataFrame(
            ...     columns=["Product", "Price"],
            ...     data=[
            ...         ("phone", 600.0),
            ...         ("headset", 80.0),
            ...         ("watch", 250.0),
            ...     ],
            ... )
            >>> table = session.read_pandas(
            ...     dataframe, keys={keys_argument}, table_name="Pandas"
            ... )
            >>> table.head().sort_index()
                     Price
            Product
            headset   80.0
            phone    600.0
            watch    250.0

        """
        arrow_table = pandas_to_arrow(dataframe, types=types)
        return self.read_arrow(
            arrow_table,
            table_name=table_name,
            keys=keys,
            partitioning=partitioning,
            types=types,
            default_values=default_values,
            **kwargs,
        )

    @doc(**_TABLE_CREATION_KWARGS, keys_argument="""{"Product"}""")
    def read_arrow(
        self,
        table: pa.Table,  # pyright: ignore[reportUnknownParameterType]
        /,
        *,
        table_name: str,
        keys: Union[AbstractSet[str], Sequence[str]] = frozenset(),
        partitioning: Optional[str] = None,
        types: Mapping[str, DataType] = frozendict(),
        default_values: Mapping[str, Optional[ConstantValue]] = frozendict(),
        **kwargs: Any,
    ) -> Table:
        """Read an Arrow Table into a table.

        Args:
            table: The Arrow Table to load.
            {table_name}
            {keys}
            {partitioning}
            types: Types for some or all columns of the table.
                Types for non specified columns will be inferred from arrow DataTypes.
            {default_values}

        Example:
            >>> import pyarrow as pa
            >>> arrow_table = pa.Table.from_arrays(
            ...     [
            ...         pa.array(["phone", "headset", "watch"]),
            ...         pa.array([600.0, 80.0, 250.0]),
            ...     ],
            ...     names=["Product", "Price"],
            ... )
            >>> arrow_table
            pyarrow.Table
            Product: string
            Price: double
            ----
            Product: [["phone","headset","watch"]]
            Price: [[600,80,250]]
            >>> table = session.read_arrow(
            ...     arrow_table, keys={keys_argument}, table_name="Arrow"
            ... )
            >>> table.head().sort_index()
                     Price
            Product
            headset   80.0
            phone    600.0
            watch    250.0

        """
        types_from_arrow = get_data_types_from_arrow(table)
        types = {**types_from_arrow, **types}
        created_table = self.create_table(
            table_name,
            types=types,
            keys=keys,
            partitioning=partitioning,
            default_values=default_values,
            **kwargs,
        )
        created_table.load_arrow(table)
        return created_table

    @doc(**_TABLE_CREATION_KWARGS)
    def read_spark(
        self,
        dataframe: SparkDataFrame,
        /,
        *,
        table_name: str,
        keys: Union[AbstractSet[str], Sequence[str]] = frozenset(),
        partitioning: Optional[str] = None,
        default_values: Mapping[str, Optional[ConstantValue]] = frozendict(),
    ) -> Table:
        """Read a Spark DataFrame into a table.

        Args:
            dataframe: The DataFrame to load.
            {table_name}
            {keys}
            {partitioning}
            {default_values}

        """
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spark"
            write_spark_to_parquet(dataframe, directory=path)
            return self.read_parquet(
                path,
                keys=keys,
                table_name=table_name,
                partitioning=partitioning,
                default_values=default_values,
            )

    @doc(
        **_TABLE_CREATION_KWARGS,
        **_CSV_KWARGS,
        **_CLIENT_SIDE_ENCRYPTION_DOC,
        columns_argument="""{"country": "Country", "area": "Region", "city": "City"}""",
        keys_argument="""{"Country"}""",
    )
    def read_csv(
        self,
        path: Union[Path, str],
        /,
        *,
        keys: Union[AbstractSet[str], Sequence[str]] = frozenset(),
        table_name: Optional[str] = None,
        separator: Optional[str] = ",",
        encoding: str = "utf-8",
        process_quotes: Optional[bool] = True,
        partitioning: Optional[str] = None,
        types: Mapping[str, DataType] = frozendict(),
        columns: Union[Mapping[str, str], Sequence[str]] = frozendict(),
        array_separator: Optional[str] = None,
        date_patterns: Mapping[str, str] = frozendict(),
        default_values: Mapping[str, Optional[ConstantValue]] = frozendict(),
        client_side_encryption: Optional[ClientSideEncryptionConfig] = None,
        **kwargs: Any,
    ) -> Table:
        """Read a CSV file into a table.

        Args:
            {path}
            {keys}
            table_name: The name of the table to create.
                Required when *path* is a glob pattern.
                Otherwise, defaults to the capitalized final component of the *path* argument.
            {separator}
            {encoding}
            {process_quotes}
            {partitioning}
            types: Types for some or all columns of the table.
                Types for non specified columns will be inferred from the first 1,000 lines.
            {columns}

                >>> import csv
                >>> from pathlib import Path
                >>> from tempfile import mkdtemp
                >>> directory = mkdtemp()
                >>> file_path = Path(directory) / "largest-cities.csv"
                >>> with open(file_path, "w") as csv_file:
                ...     writer = csv.writer(csv_file)
                ...     writer.writerows(
                ...         [
                ...             ("city", "area", "country", "population"),
                ...             ("Tokyo", "Kantō", "Japan", 14_094_034),
                ...             ("Johannesburg", "Gauteng", "South Africa", 4_803_262),
                ...             (
                ...                 "Barcelona",
                ...                 "Community of Madrid",
                ...                 "Madrid",
                ...                 3_223_334,
                ...             ),
                ...         ]
                ...     )

                Dropping the :guilabel:`population` column and renaming and reordering the remaining ones:

                >>> table = session.read_csv(
                ...     file_path,
                ...     columns={columns_argument},
                ...     keys={keys_argument},
                ... )
                >>> table.head().sort_index()
                                           Region          City
                Country
                Japan                       Kantō         Tokyo
                Madrid        Community of Madrid     Barcelona
                South Africa              Gauteng  Johannesburg

                Loading a headerless CSV file:

                >>> file_path = Path(directory) / "largest-cities-headerless.csv"
                >>> with open(file_path, "w") as csv_file:
                ...     writer = csv.writer(csv_file)
                ...     writer.writerows(
                ...         [
                ...             ("Tokyo", "Kantō", "Japan", 14_094_034),
                ...             ("Johannesburg", "Gauteng", "South Africa", 4_803_262),
                ...             (
                ...                 "Madrid",
                ...                 "Community of Madrid",
                ...                 "Spain",
                ...                 3_223_334,
                ...             ),
                ...         ]
                ...     )
                >>> table = session.read_csv(
                ...     file_path,
                ...     keys={keys_argument},
                ...     columns=["City", "Area", "Country", "Population"],
                ... )
                >>> table.head().sort_index()
                                      City                 Area  Population
                Country
                Japan                Tokyo                Kantō    14094034
                South Africa  Johannesburg              Gauteng     4803262
                Spain               Madrid  Community of Madrid     3223334

            {array_separator}
            {date_patterns}
            {default_values}
            {client_side_encryption}

        """
        private_parameters = CsvPrivateParameters(**kwargs)

        full_path = path
        path, pattern = split_path_and_pattern(path, ".csv", plugins=self._plugins)

        table_name = _infer_table_name(
            path=path, pattern=pattern, table_name=table_name
        )

        csv_file_format = CsvDataSource(
            load_data_into_table=self._java_api.load_data_into_table,
            discover_csv_file_format=self._java_api.discover_csv_file_format,
        ).discover_file_format(
            path,
            keys=set(keys),
            separator=separator,
            encoding=encoding,
            process_quotes=process_quotes,
            array_separator=array_separator,
            pattern=pattern,
            date_patterns=date_patterns,
            default_values={
                column_name: None if value is None else Constant(value)
                for column_name, value in default_values.items()
            },
            client_side_encryption=client_side_encryption,
            columns=columns,
            parser_thread_count=private_parameters.parser_thread_count,
            buffer_size_kb=private_parameters.buffer_size_kb,
        )
        types = {**csv_file_format.types, **types}
        process_quotes = (
            process_quotes
            if process_quotes is not None
            else csv_file_format.process_quotes
        )
        separator = separator if separator is not None else csv_file_format.separator

        table = self.create_table(
            table_name,
            types=types,
            keys=keys,
            partitioning=partitioning,
            default_values=default_values,
        )
        table.load_csv(
            full_path,
            columns=columns,
            separator=csv_file_format.separator,
            encoding=encoding,
            process_quotes=csv_file_format.process_quotes,
            array_separator=array_separator,
            date_patterns=date_patterns,
            client_side_encryption=client_side_encryption,
            parser_thread_count=private_parameters.parser_thread_count,
            buffer_size_kb=private_parameters.buffer_size_kb,
        )
        return table

    @doc(**_TABLE_CREATION_KWARGS, **_PARQUET_KWARGS, **_CLIENT_SIDE_ENCRYPTION_DOC)
    def read_parquet(
        self,
        path: Union[Path, str],
        /,
        *,
        keys: Union[AbstractSet[str], Sequence[str]] = frozenset(),
        columns: Mapping[str, str] = frozendict(),
        table_name: Optional[str] = None,
        partitioning: Optional[str] = None,
        default_values: Mapping[str, Optional[ConstantValue]] = frozendict(),
        client_side_encryption: Optional[ClientSideEncryptionConfig] = None,
    ) -> Table:
        """Read a Parquet file into a table.

        Args:
            {path}
            {keys}
            {columns}
            table_name: The name of the table to create.
                Required when *path* is a glob pattern.
                Otherwise, defaults to the capitalized final component of the *path* argument.
            {partitioning}
            {default_values}
            {client_side_encryption}

        """
        full_path = path
        path, pattern = split_path_and_pattern(path, ".parquet", plugins=self._plugins)
        table_name = _infer_table_name(
            path=path, pattern=pattern, table_name=table_name
        )

        inferred_types = ParquetDataSource(
            load_data_into_table=self._java_api.load_data_into_table,
            infer_types=self._java_api.infer_table_types_from_source,
        ).infer_parquet_types(
            path,
            keys=set(keys),
            pattern=pattern,
            client_side_encryption=client_side_encryption,
            columns=columns,
            default_values={
                column_name: None if value is None else Constant(value)
                for column_name, value in default_values.items()
            },
        )

        table = self.create_table(
            table_name,
            types=inferred_types,
            keys=keys,
            partitioning=partitioning,
            default_values=default_values,
        )
        table.load_parquet(
            full_path, client_side_encryption=client_side_encryption, columns=columns
        )
        return table

    @doc(**_TABLE_CREATION_KWARGS)
    def read_numpy(
        self,
        array: NDArray[Any],
        /,
        *,
        columns: Sequence[str],
        table_name: str,
        keys: Union[AbstractSet[str], Sequence[str]] = frozenset(),
        partitioning: Optional[str] = None,
        types: Mapping[str, DataType] = frozendict(),
        default_values: Mapping[str, Optional[ConstantValue]] = frozendict(),
    ) -> Table:
        """Read a NumPy 2D array into a new table.

        Args:
            array: The NumPy 2D ndarray to read the data from.
            columns: The names to use for the table's columns.
                They must be in the same order as the values in the NumPy array.
            {table_name}
            {keys}
            {partitioning}
            types: Types for some or all columns of the table.
                Types for non specified columns will be inferred from numpy data types.
            {default_values}

        """
        dataframe = pd.DataFrame(array, columns=list(columns))
        return self.read_pandas(
            dataframe,
            table_name=table_name,
            keys=keys,
            partitioning=partitioning,
            types=types,
            default_values=default_values,
        )

    @doc(**_TABLE_CREATION_KWARGS, **_SQL_KWARGS, keys_argument="""{"ID"}""")
    def read_sql(
        self,
        sql: str,
        /,
        *,
        url: str,
        table_name: str,
        driver: Optional[str] = None,
        keys: Union[AbstractSet[str], Sequence[str]] = frozenset(),
        partitioning: Optional[str] = None,
        types: Mapping[str, DataType] = frozendict(),
        default_values: Mapping[str, Optional[ConstantValue]] = frozendict(),
    ) -> Table:
        """Create a table from the result of the passed SQL query.

        Note:
            This method requires the :mod:`atoti-sql <atoti_sql>` plugin.

        Args:
            {sql}
            {url}
            {driver}
            {table_name}
            {keys}
            {partitioning}
            types: Types for some or all columns of the table.
                Types for non specified columns will be inferred from the SQL types.
            {default_values}

        Example:
            .. doctest:: read_sql

                >>> table = session.read_sql(
                ...     "SELECT * FROM MYTABLE;",
                ...     url=f"h2:file:{{RESOURCES}}/h2-database;USER=root;PASSWORD=pass",
                ...     table_name="Cities",
                ...     keys={keys_argument},
                ... )
                >>> len(table)
                5

            .. doctest:: read_sql
                :hide:

                Remove the edited H2 database from Git's working tree.
                >>> session.close()
                >>> import os
                >>> os.system(f"git checkout -- {{RESOURCES}}/h2-database.mv.db")
                0

        """
        inferred_types = self._infer_sql_types(
            sql,
            url=url,
            driver=driver,
            keys=set(keys),
            default_values=default_values,
            java_api=self._java_api,
        )
        types = {**inferred_types, **types}
        table = self.create_table(
            table_name,
            types=types,
            keys=keys,
            partitioning=partitioning,
            default_values=default_values,
        )
        table.load_sql(sql, url=url, driver=driver)
        return table

    @property
    def ready(self) -> bool:
        """Whether the session is ready or not.

        When ``False``, the server will reject most requests made by users without the :guilabel:`ROLE_ADMIN` role with an HTTP `503 Service Unavailable` status.

        Note:
            This property has no impact in the community edition since the :guilabel:`ROLE_ADMIN` role is always granted.

        This can be used to prevent queries from being made on a session that has not finished its initial setup process (tables and cubes creation, data loading, etc).
        """
        return self._java_api.get_readiness()

    @ready.setter
    def ready(self, ready: bool, /) -> None:
        return self._java_api.set_readiness(ready)

    def start_transaction(
        self, scenario_name: str = _BASE_SCENARIO_NAME
    ) -> Transaction:
        """Start a transaction to batch several table operations.

        * It is more efficient than doing each table operation one after the other.
        * It avoids possibly incorrect intermediate states (e.g. if loading some new data requires dropping existing rows first).

        Note:
            Some operations are not allowed during a transaction:

            * Long-running operations such as :meth:`atoti.Table.load_kafka`.
            * Operations changing the structure of the session's tables such as :meth:`atoti.Table.join` or :meth:`atoti.Session.read_parquet`.
            * Operations not related to data loading or dropping such as defining a new measure.
            * Operations on parameter tables created from :meth:`atoti.Cube.create_parameter_hierarchy_from_members` and :meth:`atoti.Cube.create_parameter_simulation`.
            * Operations on other source scenarios than the one the transaction is started on.

        Args:
            scenario_name: The name of the source scenario impacted by all the table operations inside the transaction.

        Example:
            >>> df = pd.DataFrame(
            ...     columns=["City", "Price"],
            ...     data=[
            ...         ("Berlin", 150.0),
            ...         ("London", 240.0),
            ...         ("New York", 270.0),
            ...         ("Paris", 200.0),
            ...     ],
            ... )
            >>> table = session.read_pandas(
            ...     df, keys=["City"], table_name="start_transaction example"
            ... )
            >>> cube = session.create_cube(table)
            >>> extra_df = pd.DataFrame(
            ...     columns=["City", "Price"],
            ...     data=[
            ...         ("Singapore", 250.0),
            ...     ],
            ... )
            >>> with session.start_transaction():
            ...     table += ("New York", 100.0)
            ...     table.drop(table["City"] == "Paris")
            ...     table.load_pandas(extra_df)
            >>> table.head().sort_index()
                       Price
            City
            Berlin     150.0
            London     240.0
            New York   100.0
            Singapore  250.0

        """
        return Transaction(
            scenario_name,
            start=self._java_api.start_transaction,
            end=self._java_api.end_transaction,
        )

    def create_cube(
        self,
        base_table: Table,
        name: Optional[str] = None,
        *,
        mode: _CubeCreationMode = "auto",
        filter: Optional[  # noqa: A002
            Condition[
                ColumnIdentifier,
                ConditionComparisonOperatorBound,
                Optional[Constant],
                ConditionCombinationOperatorBound,
            ]
        ] = None,
    ) -> Cube:
        """Create a cube based on the passed table.

        Args:
            base_table: The base table of the cube.
            name: The name of the created cube.
                Defaults to the name of the base table.
            mode: The cube creation mode:

                * ``auto``: Creates hierarchies for every key column or non-numeric column of the table, and measures for every numeric column.
                * ``manual``: Does not create any hierarchy or measure (except from the count).
                * ``no_measures``: Creates the hierarchies like ``auto`` but does not create any measures.

                Example:
                    >>> table = session.create_table(
                    ...     "Table",
                    ...     types={"id": tt.STRING, "value": tt.DOUBLE},
                    ... )
                    >>> cube_auto = session.create_cube(table)
                    >>> sorted(cube_auto.measures)
                    ['contributors.COUNT', 'update.TIMESTAMP', 'value.MEAN', 'value.SUM']
                    >>> list(cube_auto.hierarchies)
                    [('Table', 'id')]
                    >>> cube_no_measures = session.create_cube(table, mode="no_measures")
                    >>> sorted(cube_no_measures.measures)
                    ['contributors.COUNT', 'update.TIMESTAMP']
                    >>> list(cube_no_measures.hierarchies)
                    [('Table', 'id')]
                    >>> cube_manual = session.create_cube(table, mode="manual")
                    >>> sorted(cube_manual.measures)
                    ['contributors.COUNT', 'update.TIMESTAMP']
                    >>> list(cube_manual.hierarchies)
                    []

            filter: If not ``None``, only rows of the database matching this condition will be fed to the cube.
                It can also reduce costs when using DirectQuery since the filter will be applied to the queries executed on the external database to feed the cube.

                Example:
                    >>> df = pd.DataFrame(
                    ...     columns=["Product"],
                    ...     data=[
                    ...         ("phone"),
                    ...         ("watch"),
                    ...         ("laptop"),
                    ...     ],
                    ... )
                    >>> table = session.read_pandas(df, table_name="Filtered table")
                    >>> cube = session.create_cube(table, "Default")
                    >>> cube.query(
                    ...     cube.measures["contributors.COUNT"],
                    ...     levels=[cube.levels["Product"]],
                    ... )
                            contributors.COUNT
                    Product
                    laptop                   1
                    phone                    1
                    watch                    1
                    >>> filtered_cube = session.create_cube(
                    ...     table,
                    ...     "Filtered",
                    ...     filter=table["Product"].isin("watch", "laptop"),
                    ... )
                    >>> filtered_cube.query(
                    ...     filtered_cube.measures["contributors.COUNT"],
                    ...     levels=[filtered_cube.levels["Product"]],
                    ... )
                            contributors.COUNT
                    Product
                    laptop                   1
                    watch                    1

        """
        if name is None:
            name = base_table.name

        self._java_api.create_cube_from_table(
            name,
            table_identifier=base_table._identifier,
            mode=mode.upper(),
            filter=filter,
        )
        self._java_api.refresh()
        Cube(
            name,
            base_table=base_table,
            client=self._client,
            create_query_session=self._create_query_session,
            get_schema=lambda: self.tables.schema,
            java_api=self._java_api,
            load_kafka=self._load_kafka,
            load_sql=self._load_sql,
            plugins=self._plugins,
            read_pandas=self.read_pandas,
            session_name=self.name,
        )

        return self.cubes[name]

    def create_scenario(self, name: str, *, origin: str = _BASE_SCENARIO_NAME) -> None:
        """Create a new source scenario.

        Args:
            name: The name of the scenario.
            origin: The scenario to fork.
        """
        self._java_api.create_scenario(name, parent_scenario_name=origin)

    def delete_scenario(self, name: str) -> None:
        """Delete the source scenario with the provided name if it exists."""
        if name == _BASE_SCENARIO_NAME:
            raise ValueError("Cannot delete the base scenario")
        self._java_api.delete_scenario(name)

    @property
    def scenarios(self) -> Sequence[str]:
        """Names of the source scenarios of the session."""
        return self._java_api.get_scenarios()

    def _get_cube(self, cube_name: str) -> Cube:
        java_cube: Any = self._java_api.get_cube(cube_name)
        return Cube(
            java_cube.name(),
            client=self._client,
            create_query_session=self._create_query_session,
            get_schema=lambda: self.tables.schema,
            java_api=self._java_api,
            load_kafka=self._load_kafka,
            load_sql=self._load_sql,
            base_table=self.tables[java_cube.storeName()],
            plugins=self._plugins,
            read_pandas=self.read_pandas,
            session_name=self.name,
        )

    def _get_cubes(self) -> dict[str, Cube]:
        return {
            cast(Any, java_cube).name(): Cube(
                cast(Any, java_cube).name(),
                client=self._client,
                create_query_session=self._create_query_session,
                get_schema=lambda: self.tables.schema,
                java_api=self._java_api,
                load_kafka=self._load_kafka,
                load_sql=self._load_sql,
                base_table=self.tables[cast(Any, java_cube).storeName()],
                plugins=self._plugins,
                read_pandas=self.read_pandas,
                session_name=self.name,
            )
            for java_cube in self._java_api.get_cubes()
        }

    def _warn_if_license_about_to_expire(
        self,
        *,
        minimum_remaining_time: timedelta = _DEFAULT_LICENSE_MINIMUM_REMAINING_TIME,
    ) -> None:
        remaining_time = self._java_api.license_end_date - datetime.now()
        if remaining_time < minimum_remaining_time:
            message = f"""The{" embedded " if self._java_api.is_community_license else " "}license key is about to expire, {"update to Atoti's latest version or request an evaluation license key" if self._java_api.is_community_license else "contact ActiveViam to get a new license key"} in the coming {remaining_time.days} days."""
            warn(
                message,
                category=FutureWarning,
                stacklevel=2,
            )

    # Do not make this method public until it asserts that the remote session's Py4J is secured with an `auth_token`.
    @staticmethod
    def _connect(
        address: str,
        /,
        *,
        py4j_server_port: Optional[int] = None,
    ) -> Session:
        """Connect the Python API to an already running session runing."""
        return Session(
            address=address,
            name=None,
            py4j_server_port=py4j_server_port,
            start_application=False,
        )
