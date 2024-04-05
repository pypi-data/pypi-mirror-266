from ..._local_cubes import LocalCubes
from .cube import DistributedCube


class DistributedCubes(LocalCubes[DistributedCube]):
    """Manage the distributed cubes."""
