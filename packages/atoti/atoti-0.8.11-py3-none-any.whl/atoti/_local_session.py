from __future__ import annotations

import logging as _logging
import os
from collections.abc import (
    Callable,
    Collection,
    Mapping,
    MutableMapping,
    MutableSet,
    Set as AbstractSet,
)
from dataclasses import replace
from datetime import timedelta
from functools import cache, cached_property
from operator import attrgetter
from pathlib import Path
from subprocess import STDOUT, CalledProcessError, check_output
from types import TracebackType
from typing import Any, Literal, Optional, TypeVar
from weakref import WeakSet

import pandas as pd
from atoti_core import (
    DEFAULT_QUERY_TIMEOUT,
    LICENSE_KEY,
    LICENSE_KEY_ENV_VAR_NAME,
    PLUGINS,
    ActiveViamClient,
    BaseSession,
    ConstantValue,
    Context,
    DataType,
    Duration,
    IdentifierT_co,
    MissingPluginError,
    Plugin,
    TableIdentifier,
    doc,
    frozendict,
)
from atoti_query import QuerySession
from atoti_query._internal import Security
from py4j.java_gateway import DEFAULT_ADDRESS
from py4j.protocol import Py4JError
from typing_extensions import Self, override

from ._basic_credentials import BasicCredentials
from ._create_branding_app_extension import create_branding_app_extension
from ._docs_utils import EXPLAIN_QUERY_DOC
from ._endpoint import EndpointHandler
from ._get_java_executable_path import get_java_executable_path
from ._is_jwt_expired import is_jwt_expired
from ._java_api import JavaApi
from ._local_cube import LocalCube
from ._local_cubes import LocalCubes
from ._query_plan import QueryAnalysis
from ._server_subprocess import ServerSubprocess
from ._supported_java_version import SUPPORTED_JAVA_VERSION
from .config._session_config import SessionConfig
from .table import _LoadKafka, _LoadSql


def _add_branding_app_extension_to_config(config: SessionConfig, /) -> SessionConfig:
    if config.branding is None:
        return config

    app_extensions = {
        **(config.app_extensions or {}),
        **create_branding_app_extension(title=config.branding.title),
    }
    # See https://github.com/pydantic/pydantic/issues/7075.
    return replace(config, app_extensions=app_extensions)  # type: ignore[misc]


def _add_plugin_app_extensions_to_config(
    config: SessionConfig, /, *, plugins: Mapping[str, Plugin]
) -> SessionConfig:
    config_app_extensions = {**(config.app_extensions or {})}
    app_extensions = config_app_extensions.copy()

    for plugin_key, plugin in plugins.items():
        for extension_name, extension_path in plugin.app_extensions.items():
            if extension_name in config_app_extensions:
                raise ValueError(
                    f"App extension `{extension_name}` is declared both in the session's configuration and in the plugin `{plugin_key}`."
                )
            if extension_name in app_extensions:
                raise ValueError(
                    f"App extension `{extension_name}` is declared in multiple plugins."
                )
            app_extensions[extension_name] = extension_path

    # See https://github.com/pydantic/pydantic/issues/7075.
    return replace(config, app_extensions=app_extensions)  # type: ignore[misc]


_LocalCubes = TypeVar("_LocalCubes", bound=LocalCubes[LocalCube[Any, Any, Any]])


class LocalSession(BaseSession[_LocalCubes, Security]):
    _closed: bool = True
    _server_subprocess: Optional[ServerSubprocess] = None

    def __init__(  # noqa: C901, PLR0912
        self,
        *,
        address: Optional[str],
        config: SessionConfig,
        distributed: bool,
        enable_py4j_auth: bool,
        license_key: Optional[str],
        name: Optional[str],
        plugins: Optional[Mapping[str, Plugin]],
        py4j_server_port: Optional[int],
        start_application: bool,
        wrap_start_error: bool,
    ):
        if address is None:
            address = DEFAULT_ADDRESS

        if plugins is None:
            plugins = PLUGINS.default

        config = _add_branding_app_extension_to_config(config)
        config = _add_plugin_app_extensions_to_config(config, plugins=plugins)

        super().__init__()

        self._address = address
        self._closed = False
        self._config = config
        self._name = name
        self._plugins = plugins
        self.__jwt: Optional[str] = None

        def load_kafka(
            identifier: TableIdentifier,  # noqa: ARG001
            /,
            bootstrap_server: str,  # noqa: ARG001
            topic: str,  # noqa: ARG001
            *,
            group_id: str,  # noqa: ARG001
            batch_duration: timedelta,  # noqa: ARG001
            consumer_config: Mapping[str, str],  # noqa: ARG001
            java_api: JavaApi,  # noqa: ARG001
            scenario_name: str,  # noqa: ARG001
        ) -> None:
            raise MissingPluginError("kafka")

        self._load_kafka: _LoadKafka = load_kafka

        def infer_sql_types(
            sql: str,  # noqa: ARG001
            /,
            *,
            url: str,  # noqa: ARG001
            driver: Optional[str] = None,  # noqa: ARG001
            keys: AbstractSet[str],  # noqa: ARG001
            default_values: Mapping[str, Optional[ConstantValue]],  # noqa: ARG001
            java_api: JavaApi,  # noqa: ARG001
        ) -> dict[str, DataType]:
            raise MissingPluginError("sql")

        self._infer_sql_types = infer_sql_types

        def load_sql(
            identifier: TableIdentifier,  # noqa: ARG001
            sql: str,  # noqa: ARG001
            /,
            *,
            url: str,  # noqa: ARG001
            driver: Optional[str] = None,  # noqa: ARG001
            java_api: JavaApi,  # noqa: ARG001
            scenario_name: str,  # noqa: ARG001
        ) -> None:
            raise MissingPluginError("sql")

        self._load_sql: _LoadSql = load_sql

        if not license_key and LICENSE_KEY.use_env_var:
            license_key = os.environ.get(LICENSE_KEY_ENV_VAR_NAME)

        _get_local_sessions().add(self)

        try:
            # Attempt to connect to an existing detached process (useful for debugging).
            # Failed attempts are very fast (usually less than 2ms): users won't notice them.
            self._java_api = JavaApi(
                address=self._address,
                auth_token=None,
                distributed=distributed,
                py4j_java_port=py4j_server_port,
            )
        # When another Atoti session already created a Py4J server on the default port, trying to attach to it without passing the right `auth_token` will raise a `Py4JError`.
        # When there are no Atoti sessions or detached processes running, there will be no Py4J server listening on the default port: a `ConnectionRefusedError` will be raised.
        except (ConnectionRefusedError, Py4JError):
            # No available unauthenticated detached process: creating subprocess.
            self._server_subprocess = ServerSubprocess(
                address=self._address,
                config=self._config,
                enable_py4j_auth=enable_py4j_auth,
                license_key=license_key,
                plugins=self._plugins,
                py4j_server_port=py4j_server_port,
                session_id=self._id,
            )
            self._java_api = JavaApi(
                address=self._address,
                auth_token=self._server_subprocess.auth_token,
                distributed=distributed,
                py4j_java_port=self._server_subprocess.py4j_java_port,
            )

        if start_application:
            plugin_java_package_names = {
                plugin.__class__.__name__: plugin.java_package_name
                for plugin in plugins.values()
                if plugin.java_package_name
            }

            if license_key:
                plugin_java_package_names["PlusPlugin"] = "io.atoti.plugins"

            for class_name, package_name in plugin_java_package_names.items():
                qualified_class_name = f"{package_name}.{class_name}"
                try:
                    init_method: Callable[[], None] = attrgetter(
                        f"{qualified_class_name}.init"
                    )(self._java_api.jvm)
                    init_method()
                except Exception as error:  # noqa: BLE001
                    raise RuntimeError(
                        f"An error occurred while initializing `{qualified_class_name}`."
                    ) from error

            if wrap_start_error:
                try:
                    self._start_application()
                except Py4JError as error:
                    raise RuntimeError(
                        f"An error occurred while starting the session. The logs are available at {self.logs_path}"
                    ) from error
            else:
                self._start_application()

    def __del__(self) -> None:
        # Use private method to avoid sending a telemetry event that would raise `RuntimeError: cannot schedule new futures after shutdown` when calling `ThreadPoolExecutor.submit()`.
        self._close()

    @cached_property
    def __client(self) -> ActiveViamClient:
        return ActiveViamClient(
            self._local_url,
            auth=lambda _url: self._generate_auth_headers(),
            certificate_authority=Path(self._config.https.certificate_authority)
            if self._config.https and self._config.https.certificate_authority
            else None,
        )

    @property
    @override
    def _client(self) -> ActiveViamClient:
        return self.__client

    @property
    def name(self) -> Optional[str]:
        """Name of the session."""
        return self._name

    @property
    def security(self) -> Security:
        return self._security

    @property
    @override
    def _security(self) -> Security:
        return self.__security

    @property
    def __security(self) -> Security:
        return Security(basic_credentials=self._basic_credentials, client=self._client)

    @property
    def closed(self) -> bool:
        """Return whether the session is closed or not."""
        return self._closed

    @property
    def port(self) -> int:
        """Port on which the session is exposed.

        Can be configured with :func:`atoti.Session`'s *port*  parameter.

        See Also:
            :attr:`atoti.Session.link` to display a link to this session.
        """
        return self._java_api.get_session_port()

    @property
    def logs_path(self) -> Path:
        """Path to the session logs file."""
        if self._server_subprocess is None:
            raise RuntimeError(
                "The logs path is not available when using a detached server process."
            )

        return self._server_subprocess.logs_path

    def _start_application(self) -> None:
        self._java_api.start_application(self._config)

    def __enter__(self) -> Self:
        assert (
            not self.closed
        ), "Cannot re-enter a session that has already been closed."
        return self

    def __exit__(  # pylint: disable=too-many-positional-parameters
        self,
        exception_type: Optional[type[BaseException]],
        exception_value: Optional[BaseException],
        exception_traceback: Optional[TracebackType],
    ) -> None:
        if not self.closed:
            self.close()

    def _clear(self) -> None:
        """Clear this session and free all the associated resources."""
        self._java_api.clear_session()

    def _close(self) -> None:
        if self.closed:
            return

        try:
            if self._server_subprocess:
                self._java_api.shutdown()
                self._server_subprocess.wait()
        finally:
            self._closed = True
            _get_local_sessions().discard(self)

    def close(self) -> None:
        """Close this session and free all the associated resources."""
        self._close()

    def wait(self) -> None:
        """Wait for the underlying server subprocess to terminate.

        This will prevent the Python process to exit.
        """
        if self._server_subprocess is None:
            raise RuntimeError("Cannot wait on a detached server process.")

        self._server_subprocess.wait()

    @property
    @override
    def _location(self) -> Mapping[str, object]:
        return {
            "https": self._config.https is not None,
            "port": self.port,
        }

    @property
    def _basic_credentials(self) -> Optional[MutableMapping[str, str]]:
        return BasicCredentials(java_api=self._java_api)

    @property
    @override
    def _local_url(self) -> str:
        address = "localhost"
        protocol = "http"

        if self._address != DEFAULT_ADDRESS:
            address = self._address

        if self._config.https:
            address = self._config.https.domain
            protocol = "https"

        return f"{protocol}://{address}:{self.port}"

    def _generate_token(self) -> str:
        """Return a token that can be used to authenticate against the server."""
        return self._java_api.generate_jwt()

    @override
    def _block_until_widget_loaded(self, widget_id: str) -> None:
        self._java_api.block_until_widget_loaded(widget_id)

    def _create_query_session(self) -> QuerySession:
        return QuerySession(
            self._local_url,
            client=self._client,  # Sharing the client to avoid refetching the server versions.
        )

    @override
    def query_mdx(
        self,
        mdx: str,
        *,
        keep_totals: bool = False,
        timeout: Duration = DEFAULT_QUERY_TIMEOUT,
        mode: Literal["pretty", "raw"] = "pretty",
        context: Context = frozendict(),
    ) -> pd.DataFrame:
        def get_data_types(
            identifiers: Collection[IdentifierT_co], /, *, cube_name: str
        ) -> dict[IdentifierT_co, DataType]:
            return self.cubes[cube_name]._get_data_types(identifiers)

        return self._create_query_session().query_mdx(
            mdx,
            get_data_types=get_data_types,
            keep_totals=keep_totals,
            timeout=timeout,
            session=self,
            mode=mode,
            context=context,
        )

    @doc(EXPLAIN_QUERY_DOC, corresponding_method="query_mdx")
    def explain_mdx_query(
        self, mdx: str, *, timeout: Duration = DEFAULT_QUERY_TIMEOUT
    ) -> QueryAnalysis:
        return self._java_api.analyze_mdx(mdx, timeout=timeout)

    @override
    def _generate_auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Jwt {self._jwt}"}

    @property
    def _jwt(self) -> str:
        if not self.__jwt or is_jwt_expired(self.__jwt):
            self.__jwt = self._java_api.generate_jwt()
        return self.__jwt

    def endpoint(
        self, route: str, *, method: Literal["POST", "GET", "PUT", "DELETE"] = "GET"
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Create a custom endpoint at ``/atoti/pyapi/{route}``.

        This is useful to reuse Atoti's built-in server instead of adding a `FastAPI <https://fastapi.tiangolo.com/>`__ or `Flask <https://flask.palletsprojects.com/>`__ server to the project.
        This way, when deploying the project in a container or a VM, only one port (the one of the Atoti server) can be exposed instead of two.
        Since custom endpoints are exposed by Atoti's server, they automatically inherit from the configured :func:`atoti.Session`'s *authentication* and *https* parameter.

        The decorated function must take three parameters with types :class:`atoti.pyapi.User`, :class:`atoti.pyapi.HttpRequest`, and :class:`atoti.Session` and return a response body as a Python data structure that can be converted to JSON.

        Args:
            route: The path suffix after ``/atoti/pyapi/``.
                For instance, if ``custom/search`` is passed, a request to ``/atoti/pyapi/custom/search?query=test#results`` will match.
                The route should not contain the query (``?``) or fragment (``#``).

                Path parameters can be configured by wrapping their name in curly braces in the route.
            method: The HTTP method the request must be using to trigger this endpoint.
                ``DELETE``, ``POST``, and ``PUT`` requests can have a body but it must be JSON.

        Example:
            .. doctest:: Session.endpoint
                :skipif: True

                >>> import requests
                >>> df = pd.DataFrame(
                ...     columns=["Year", "Month", "Day", "Quantity"],
                ...     data=[
                ...         (2019, 7, 1, 15),
                ...         (2019, 7, 2, 20),
                ...     ],
                ... )
                >>> table = session.read_pandas(df, table_name="Quantity")
                >>> table.head()
                Year  Month  Day  Quantity
                0  2019      7    1        15
                1  2019      7    2        20
                >>> endpoints_base_url = f"http://localhost:{session.port}/atoti/pyapi"
                >>> @session.endpoint("tables/{table_name}/size", method="GET")
                ... def get_table_size(request, user, session):
                ...     table_name = request.path_parameters["table_name"]
                ...     return len(session.tables[table_name])
                >>> requests.get(f"{endpoints_base_url}/tables/Quantity/size").json()
                2
                >>> @session.endpoint("tables/{table_name}/rows", method="POST")
                ... def append_rows_to_table(request, user, session):
                ...     rows = request.body
                ...     table_name = request.path_parameters["table_name"]
                ...     session.tables[table_name].append(*rows)
                >>> requests.post(
                ...     f"{endpoints_base_url}/tables/Quantity/rows",
                ...     json=[
                ...         {"Year": 2021, "Month": 5, "Day": 19, "Quantity": 50},
                ...         {"Year": 2021, "Month": 5, "Day": 20, "Quantity": 6},
                ...     ],
                ... ).status_code
                200
                >>> requests.get(f"{endpoints_base_url}/tables/Quantity/size").json()
                4
                >>> table.head()
                Year  Month  Day  Quantity
                0  2019      7    1        15
                1  2019      7    2        20
                2  2021      5   19        50
                3  2021      5   20         6

        """
        if route[0] == "/" or "?" in route or "#" in route:
            raise ValueError(
                f"Invalid route '{route}'. It should not start with '/' and not contain '?' or '#'."
            )

        def endpoint_decorator(callback: Callable[..., Any]) -> Callable[..., Any]:
            self._java_api.create_endpoint(
                http_method=method,
                route=route,
                handler=EndpointHandler(callback, session=self),
            )
            return callback

        return endpoint_decorator

    def export_translations_template(self, path: Path) -> None:
        """Export a template containing all translatable values in the session's cubes.

        Args:
            path: The path at which to write the template.
        """
        self._java_api.export_i18n_template(path)

    def _get_jfr_command(self, jfr_action: str, /, *args: str) -> list[str]:
        if self._server_subprocess is None:
            raise RuntimeError("Cannot create flight recording with detached process.")

        return [
            str(
                get_java_executable_path(
                    executable_name="jcmd",
                    supported_java_version=SUPPORTED_JAVA_VERSION,
                )
            ),
            str(self._server_subprocess.pid),
            f"JFR.{jfr_action}",
            *args,
        ]

    def _create_memory_analysis_report(self, directory: Path, /) -> None:
        """Create a memory analysis report.

        Args:
            directory: The path of the directory where the report will be created.
              Its parent directory must already exist.
        """
        assert directory.parent.is_dir()
        self._java_api.memory_analysis_export(directory.parent, directory.name)

    def _create_flight_recording(self, path: Path, /, *, duration: Duration) -> None:
        """Create a recording file using Java Flight Recorder (JFR).

        This call is non-blocking: ``jcmd`` will continue writing to the file at the specified *path* for the given *duration* after this function returns.
        Call :func:`time.sleep` with ``duration.total_seconds()`` to block the current thread until the end of the recording.

        Args:
            path: The path (with a :guilabel:`.jfr` extension) at which the recording file should be written to.
            duration: The duration of the recording.
        """
        command = self._get_jfr_command(
            "start",
            f"duration={int(duration.total_seconds())}s",
            f"filename={path}",
        )

        try:
            check_output(
                command,  # noqa: S603
                stderr=STDOUT,
                text=True,
            )
        except CalledProcessError as error:
            raise RuntimeError(
                f"Failed to create flight recording:\n{error.output}"
            ) from error

    @override
    def __repr__(self) -> str:
        info: dict[str, object] = {"port": self.port}

        if self._server_subprocess:
            info["logs_path"] = self._server_subprocess.logs_path

        return repr(info)


LocalSessionBound = LocalSession[Any]


class _LocalSessions(WeakSet[LocalSessionBound]):
    @override
    def add(self, item: LocalSessionBound) -> None:
        if item.name is not None:
            existing_session = next(
                (
                    other_session
                    for other_session in self
                    if other_session.name == item.name
                ),
                None,
            )
            if existing_session:
                _logging.getLogger("atoti").warning(
                    """Closing existing "%s" session to create the new one.""",
                    item.name,
                )
                existing_session.close()

        super().add(item)


@cache
def _get_local_sessions() -> MutableSet[LocalSessionBound]:
    return _LocalSessions()
