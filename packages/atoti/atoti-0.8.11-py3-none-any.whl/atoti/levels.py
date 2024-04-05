from typing import Optional

from atoti_core import BaseLevels, LevelKey
from py4j.protocol import Py4JError
from typing_extensions import override

from .hierarchies import Hierarchies
from .level import Level


class Levels(BaseLevels[Hierarchies, Level]):
    r"""Flat representation of all the :class:`~atoti.Level`\ s in a :class:`~atoti.Cube`."""

    def __delitem__(self, key: LevelKey, /) -> None:
        """Delete a level.

        Args:
            key: The name of the level to delete, or a ``(hierarchy_name, level_name)`` tuple.
        """
        if key not in self:
            raise KeyError(f"{key} is not an existing level.")
        level = self[key]
        level._java_api.delete_level(level._identifier, cube_name=level._cube_name)
        level._java_api.refresh()

    @override
    def _find_level(
        self,
        level_name: str,
        *,
        dimension_name: Optional[str] = None,
        hierarchy_name: Optional[str] = None,
    ) -> Level:
        try:
            hierarchy_argument = self._hierarchies._java_api.find_level_hierarchy(
                level_name,
                cube_name=self._hierarchies._cube_name,
                dimension_name=dimension_name,
                hierarchy_name=hierarchy_name,
            )
        except Py4JError as error:
            raise KeyError(str(error)) from None
        hierarchy = self._hierarchies._create_hierarchy_from_arguments(
            hierarchy_argument
        )
        return hierarchy.levels[level_name]
