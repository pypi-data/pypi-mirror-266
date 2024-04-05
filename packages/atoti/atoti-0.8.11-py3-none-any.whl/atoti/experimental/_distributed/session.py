from __future__ import annotations

from collections.abc import Collection, Mapping
from typing import Any, Optional, cast

from atoti_core import PLUGINS, Plugin
from typing_extensions import override

from ..._local_session import LocalSession
from ...config._session_config import SessionConfig
from .cube import DistributedCube
from .cubes import DistributedCubes
from .discovery_protocol import DiscoveryProtocol


class DistributedSession(LocalSession[DistributedCubes]):
    """Holds a connection to the Java gateway."""

    def __init__(
        self,
        *,
        config: Optional[SessionConfig] = None,
        license_key: Optional[str] = None,
        plugins: Optional[Mapping[str, Plugin]] = None,
    ):
        """Create the session and the Java gateway."""
        super().__init__(
            address=None,
            config=config or SessionConfig(),
            enable_py4j_auth=True,
            distributed=True,
            license_key=license_key,
            name=None,
            plugins=plugins,
            py4j_server_port=None,
            start_application=True,
            wrap_start_error=True,
        )

        self._cubes = DistributedCubes(
            delete_cube=self._java_api.delete_cube,
            get_cube=self._get_cube,
            get_cubes=self._get_cubes,
        )

        plugins = PLUGINS.default if plugins is None else plugins
        for plugin in plugins.values():
            plugin.post_init_session(self)

    @property
    @override
    def cubes(self) -> DistributedCubes:
        """Cubes of the session."""
        return self._cubes

    def create_cube(
        self,
        name: str,
        *,
        cube_url: Optional[str] = None,
        cube_port: Optional[int] = None,
        discovery_protocol: Optional[DiscoveryProtocol] = None,
        distributing_levels: Collection[str] = (),
    ) -> DistributedCube:
        """Create a distributed cube.

        Args:
            name: The name of the created cube.
            cube_url: The URL of the cube.
            cube_port: The port of the cube.
            discovery_protocol: The protocol used to discover the nodes of the cluster.
            distributing_levels: The name of the levels partitioning the data within the cluster.
        """
        discovery_protocol_xml = (
            None if discovery_protocol is None else discovery_protocol._xml
        )
        self._java_api.create_distributed_cube(
            cube_name=name,
            cube_url=cube_url,
            cube_port=cube_port,
            discovery_protocol_xml=discovery_protocol_xml,
            distributing_levels=distributing_levels,
        )
        self._java_api.java_api.refresh()
        return DistributedCube(
            name,
            client=self._client,
            create_query_session=self._create_query_session,
            java_api=self._java_api,
            session_name=self.name,
        )

    def _get_cube(self, cube_name: str) -> DistributedCube:
        java_cube = self._java_api.get_cube(cube_name)
        return DistributedCube(
            cast(Any, java_cube).name(),
            client=self._client,
            create_query_session=self._create_query_session,
            java_api=self._java_api,
            session_name=self.name,
        )

    def _get_cubes(self) -> dict[str, DistributedCube]:
        return {
            cast(Any, java_cube).name(): DistributedCube(
                cast(Any, java_cube).name(),
                client=self._client,
                create_query_session=self._create_query_session,
                java_api=self._java_api,
                session_name=self.name,
            )
            for java_cube in self._java_api.get_cubes()
        }
