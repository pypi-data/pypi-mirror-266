"""Atoti supports distributed clusters with several data cubes and one query cube.

This is not the same as a query session: in a query session, the query cube connects to a remote data cube and query its content, while in a distributed setup, multiple data cubes can join a distributed cluster where a distributed cube can be queried to retrieve the union of their data.
"""

from .cube import DistributedCube as DistributedCube
from .discovery_protocol import DiscoveryProtocol as DiscoveryProtocol
from .join_distributed_cluster import (
    join_distributed_cluster as join_distributed_cluster,
)
from .session import DistributedSession as DistributedSession
