from __future__ import annotations

import os
import platform
from collections.abc import Mapping
from io import TextIOBase
from pathlib import Path
from subprocess import PIPE, STDOUT, Popen
from threading import Thread
from typing import IO, Optional, Union

from atoti_core import LICENSE_KEY_ENV_VAR_NAME, Plugin

from ._get_java_executable_path import get_java_executable_path
from ._path import DATA_DIRECTORY
from ._path_utils import get_atoti_home
from ._supported_java_version import SUPPORTED_JAVA_VERSION
from ._wait_for_matching_output import wait_for_matching_output
from .config._session_config import SessionConfig

_COMMUNITY_LICENSE_KEY_PATH = DATA_DIRECTORY / "community.lic"


JAR_PATH = DATA_DIRECTORY / "atoti.jar"

_DEFAULT_HADOOP_PATH = Path(__file__).parent / "bin" / "hadoop-3.2.1"

# Keep in sync with Java's ApplicationStarter.ENABLE_AUTH_OPTION.
_ENABLE_AUTH_OPTION = "--enable-auth"
# Keep in sync with Java's ApplicationStarter.BIND_ADDRESS_ARGUMENT
_BIND_ADDRESS_ARGUMENT = "--bind-address"

# Keep in sync with Java's ServerUtils.serverStarted().
_PY4J_SERVER_STARTED_PATTERN = (
    r"Py4J server started on port (?P<port>\d+)(?: with auth token (?P<token>.+))?$"
)


def _get_logs_directory(session_directory: Path) -> Path:
    return session_directory / "logs"


def _create_session_directory(*, session_id: str) -> Path:
    session_directory = get_atoti_home() / session_id
    _get_logs_directory(session_directory).mkdir(parents=True)
    return session_directory


def _get_command(
    *,
    address: Optional[str],
    config: SessionConfig,
    enable_py4j_auth: bool,
    java_executable_path: Path,
    plugins: Mapping[str, Plugin],
    py4j_server_port: Optional[int],
    session_directory: Path,
) -> list[str]:
    command: list[str] = [
        str(java_executable_path),
        "-jar",
        # Arrow reflexive access : https://github.com/activeviam/activepivot/pull/4297/files#diff-d9ef6fa90dda49aa1ec2907eba7be19c916c5f553c9846b365d30a307740aea2
        "--add-opens=java.base/java.nio=ALL-UNNAMED",
        # Py4J reflexive access : java.lang.reflect.InaccessibleObjectException: Unable to make public java.lang.Object[] java.util.HashMap$KeySet.toArray() accessible: module java.base does not "opens java.util" to unnamed module @647fd8ce
        "--add-opens=java.base/java.util=ALL-UNNAMED",
        "--add-opens=java.base/java.lang=ALL-UNNAMED",
        f"-Dserver.port={config.port}",
        f"-Dserver.session_directory={session_directory}",
        "-Dactiveviam.feature.experimental.experimental_copper.enabled=true",  # spell-checker: disable-line
        # Remove following line in 0.9.0.
        "-Dactiveviam.feature.experimental.copper_in_distributed_cube.enabled=true",  # spell-checker: disable-line
        # The user is allowed to pass any options to Java, even dangerous ones.
        *config.java_options,
    ]

    if not config.logging or not config.logging._destination_io:
        command.append("-Dserver.logging.disable_console_logging=true")

    if platform.system() == "Windows":
        command.append(f"-Dhadoop.home.dir={_DEFAULT_HADOOP_PATH}")
        hadoop_path = str(_DEFAULT_HADOOP_PATH / "bin")
        if hadoop_path not in os.environ["PATH"]:
            os.environ["PATH"] = f"{os.environ['PATH']};{hadoop_path}"

    jar_paths = [
        *[
            jar_path
            for jar_path in DATA_DIRECTORY.glob("*.jar")
            if jar_path != JAR_PATH
        ],
        *(config.extra_jars),
        *[plugin.jar_path for plugin in plugins.values() if plugin.jar_path],
    ]
    if len(jar_paths) > 0:
        command.append(
            f"-Dloader.path={','.join([str(jar_path) for jar_path in jar_paths])}"
        )

    if py4j_server_port is not None:
        command.append(f"-Dpy4j.port={py4j_server_port}")

    command.append(str(JAR_PATH))

    if address is not None:
        command.append(f"{_BIND_ADDRESS_ARGUMENT}={address}")

    if enable_py4j_auth:
        command.append(_ENABLE_AUTH_OPTION)

    return command


def _copy_stream(
    input_stream: IO[str], output_stream: Optional[Union[IO[str], TextIOBase]] = None
) -> None:
    for line in input_stream:
        if output_stream and not output_stream.closed:
            output_stream.write(line)
        else:
            # When no output stream is passed, the input stream is still iterated upon to avoid blocking it but nothing is done with its lines.
            ...
    if not input_stream.closed:
        input_stream.close()


class ServerSubprocess:
    def __init__(
        self,
        *,
        address: str,
        config: SessionConfig,
        enable_py4j_auth: bool,
        license_key: Optional[str],
        plugins: Mapping[str, Plugin],
        py4j_server_port: Optional[int],
        session_id: str,
    ):
        self._config = config
        self._session_directory = _create_session_directory(session_id=session_id)

        java_executable_path = get_java_executable_path(
            supported_java_version=SUPPORTED_JAVA_VERSION
        )

        command = _get_command(
            address=address,
            config=config,
            enable_py4j_auth=enable_py4j_auth,
            java_executable_path=java_executable_path,
            plugins=plugins,
            py4j_server_port=py4j_server_port,
            session_directory=self._session_directory,
        )

        if not license_key:
            assert _COMMUNITY_LICENSE_KEY_PATH.exists()
            license_key = str(_COMMUNITY_LICENSE_KEY_PATH)

        self._process = Popen(
            command,  # noqa: S603
            env={**os.environ, LICENSE_KEY_ENV_VAR_NAME: license_key},
            stderr=STDOUT,
            stdout=PIPE,
            text=True,
        )

        match, startup_output = wait_for_matching_output(
            _PY4J_SERVER_STARTED_PATTERN,
            process=self._process,
        )

        self.py4j_java_port = int(match.group("port"))
        self.auth_token: Optional[str] = match.group("token")

        logging_destination_io = config.logging and config.logging._destination_io

        if logging_destination_io:
            logging_destination_io.write(startup_output)
        else:
            startup_log_path = (
                _get_logs_directory(self._session_directory) / "startup.log"
            )
            startup_log_path.write_text(startup_output, encoding="utf8")

        self._output_copier = Thread(
            target=_copy_stream,
            args=(self._process.stdout, logging_destination_io),
            daemon=True,
        )
        self._output_copier.start()

    def wait(self) -> None:
        """Wait for the process to terminate.

        This will prevent the Python process from exiting.
        If the Py4J gateway is closed the Atoti server will stop itself anyway.
        """
        self._process.wait()
        self._output_copier.join()

    @property
    def pid(self) -> int:
        return self._process.pid

    @property
    def logs_path(self) -> Path:
        if self._config.logging and self._config.logging._destination_io:
            raise RuntimeError(
                "Logs have been configured to be written to a specified IO."
            )

        if self._config.logging and self._config.logging.destination:
            if not isinstance(self._config.logging.destination, (str, Path)):
                raise TypeError(
                    f"Unexpected logging destination type: `{type(self._config.logging.destination).__name__}`."
                )

            return Path(self._config.logging.destination)

        return _get_logs_directory(self._session_directory) / "server.log"
