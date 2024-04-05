from ._local_cubes import LocalCubes
from .cube import Cube


class Cubes(LocalCubes[Cube]):
    r"""Manage the :class:`~atoti.Cube`\ s of a :class:`~atoti.Session`."""
