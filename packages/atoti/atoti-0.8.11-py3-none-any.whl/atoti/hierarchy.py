from __future__ import annotations

from collections.abc import Mapping, MutableMapping

from atoti_core import BaseHierarchy, HierarchyIdentifier, LevelIdentifier
from pydantic import JsonValue
from typing_extensions import override

from ._hierarchy_properties import HierarchyProperties
from ._java_api import JavaApi
from ._level_arguments import LevelArguments
from .level import Level


class Hierarchy(BaseHierarchy[Level]):
    """Hierarchy of a :class:`~atoti.Cube`.

    A hierarchy is a sub category of a :attr:`~dimension` and represents a precise type of data.

    For example, :guilabel:`Quarter` or :guilabel:`Week` could be hierarchies in the :guilabel:`Time` dimension.

    See Also:
        :class:`~atoti.hierarchies.Hierarchies` to define one.
    """

    def __init__(
        self,
        identifier: HierarchyIdentifier,
        /,
        *,
        cube_name: str,
        java_api: JavaApi,
        levels_arguments: Mapping[str, LevelArguments],
        slicing: bool,
        visible: bool,
        virtual: bool,
        dimension_default: bool,
    ) -> None:
        super().__init__(identifier)

        self._cube_name = cube_name
        self._java_api = java_api
        self._slicing = slicing
        self._visible = visible
        self._virtual = virtual
        self._dimension_default = dimension_default

        self._levels: Mapping[str, Level] = {
            level_name: Level(
                LevelIdentifier(identifier, level_name),
                column_identifier=level_arguments[1],
                cube_name=self._cube_name,
                data_type=level_arguments[2],
                java_api=self._java_api,
            )
            for level_name, level_arguments in levels_arguments.items()
        }

    @property
    @override
    def levels(self) -> Mapping[str, Level]:
        return self._levels

    @property
    def virtual(self) -> bool:
        """Whether the hierarchy is virtual or not.

        A virtual hierarchy is a lightweight hierarchy which does not store in memory the list of its members.
        It is useful for hierarchies with large cardinality.
        """
        return self._virtual

    @virtual.setter
    def virtual(self, virtual: bool, /) -> None:
        self._java_api.update_hierarchy_virtual(
            self._identifier,
            virtual,
            cube_name=self._cube_name,
        )
        self._java_api.refresh()
        self._virtual = virtual

    @property
    def dimension_default(self) -> bool:
        """Whether the hierarchy is the default in its :attr:`~atoti.Hierarchy.dimension` or not.

        Some UIs support clicking on a dimension (or drag and dropping it) as a shortcut to add its default hierarchy to a widget.

        Example:
            >>> table = session.create_table(
            ...     "Sales",
            ...     types={
            ...         "Product": tt.STRING,
            ...         "Shop": tt.STRING,
            ...         "Customer": tt.STRING,
            ...         "Date": tt.LOCAL_DATE,
            ...     },
            ... )
            >>> cube = session.create_cube(table, mode="manual")
            >>> h = cube.hierarchies
            >>> for name in table.columns:
            ...     h[name] = [table[name]]
            ...     assert h[name].dimension == table.name

            By default, the default hierarchy of a dimension is the first created one:

            >>> h["Product"].dimension_default
            True
            >>> h["Shop"].dimension_default
            False
            >>> h["Customer"].dimension_default
            False
            >>> h["Date"].dimension_default
            False

            There can only be one default hierarchy per dimension:

            >>> h["Shop"].dimension_default = True
            >>> h["Product"].dimension_default
            False
            >>> h["Shop"].dimension_default
            True
            >>> h["Customer"].dimension_default
            False
            >>> h["Date"].dimension_default
            False

            When the default hierarchy is deleted, the first created remaining one becomes the default:

            >>> del h["Shop"]
            >>> h["Product"].dimension_default
            True
            >>> h["Customer"].dimension_default
            False
            >>> h["Date"].dimension_default
            False

            The same thing occurs if the default hierarchy is moved to another dimension:

            >>> h["Product"].dimension = "Product"
            >>> h["Customer"].dimension_default
            True
            >>> h["Date"].dimension_default
            False

            Since :guilabel:`Product` is the first created hierarchy of the newly created dimension, it is the default one there:

            >>> h["Product"].dimension_default
            True

        """
        return self._dimension_default

    @dimension_default.setter
    def dimension_default(self, dimension_default: bool, /) -> None:
        self._java_api.set_hierarchy_dimension_default(
            self._identifier,
            dimension_default,
            cube_name=self._cube_name,
        )
        self._java_api.refresh()
        self._dimension_default = dimension_default

    # mypy does not detect the decorator just below.
    @property  # type: ignore[explicit-override]
    @override
    def dimension(self) -> str:
        """Name of the dimension of the hierarchy.

        Note:
            If all the hierarchies in a dimension have their deepest level of type ``TIME``, the dimension's type will be set to ``TIME`` too.
            This can be useful for some clients such as Excel which rely on the dimension's type to be ``TIME`` to decide whether to display date filters.
        """
        return self._identifier.dimension_name

    @dimension.setter
    def dimension(self, value: str, /) -> None:
        self._java_api.update_hierarchy_dimension(
            self._identifier,
            value,
            cube_name=self._cube_name,
        )
        self._java_api.refresh()
        self._BaseHierarchy__identifier = HierarchyIdentifier(value, self.name)

    # mypy does not detect the decorator just below.
    @property  # type: ignore[explicit-override]
    @override
    def slicing(self) -> bool:
        return self._slicing

    @slicing.setter
    def slicing(self, value: bool, /) -> None:
        """Slicing setter."""
        self._java_api.update_hierarchy_slicing(
            self._identifier,
            value,
            cube_name=self._cube_name,
        )
        self._java_api.refresh()
        self._slicing = value

    @property
    def visible(self) -> bool:
        """Whether the hierarchy is visible or not."""
        return self._visible

    @visible.setter
    def visible(self, value: bool, /) -> None:
        """Visibility setter."""
        self._java_api.set_hierarchy_visibility(
            self._identifier, value, cube_name=self._cube_name
        )
        self._java_api.refresh()
        self._visible = value

    @property
    def _properties(self) -> MutableMapping[str, JsonValue]:
        return HierarchyProperties(
            cube_name=self._cube_name,
            hierarchy_identifier=self._identifier,
            java_api=self._java_api,
        )
