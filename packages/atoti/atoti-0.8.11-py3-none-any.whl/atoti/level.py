from __future__ import annotations

from collections.abc import MutableMapping

from atoti_core import (
    BaseLevel,
    ColumnIdentifier,
    DataType,
    Identifiable,
    LevelIdentifier,
    ReprJson,
)
from typing_extensions import override

from ._java_api import JavaApi
from ._member_properties import MemberProperties
from .order._order import Order


class Level(BaseLevel):
    """Level of a :class:`~atoti.Hierarchy`.

    A level is a sub category of a hierarchy.
    Levels have a specific order with a parent-child relationship.

    In a :guilabel:`Pivot Table`, a single-level hierarchy will be displayed as a flat attribute while a multi-level hierarchy will display the first level and allow users to expand each member against the next level and display sub totals.

    For example, a :guilabel:`Geography` hierarchy can have a :guilabel:`Continent` as the top level where :guilabel:`Continent` expands to :guilabel:`Country` which in turn expands to the leaf level: :guilabel:`City`.
    """

    def __init__(
        self,
        identifier: LevelIdentifier,
        /,
        *,
        column_identifier: ColumnIdentifier,
        cube_name: str,
        data_type: DataType,
        java_api: JavaApi,
    ) -> None:
        super().__init__(identifier)

        self._column_identifier = column_identifier
        self._cube_name = cube_name
        self._data_type: DataType = data_type
        self._java_api = java_api

    @property
    def data_type(self) -> DataType:
        """Type of the level members."""
        return self._data_type

    @property
    def _member_properties(self) -> MutableMapping[str, Identifiable[ColumnIdentifier]]:
        """The custom properties of the members of this level.

        Member properties allow to attach some attributes to a member without creating dedicated levels.
        The properties can be requested in MDX queries.

        The keys in the mapping are the names of the custom properties.
        The values are table columns from which property values will be read.
        These columns can come from different tables.
        These tables do not have to be joined but they must have either:

        * a single key column
        * as many key columns as the number of levels of this level's hierarchy (not implemented yet)

        These keys columns will be used to determine which table row corresponds to which level member.
        If a member does not have a corresponding table row, the property value will be ``None``.

        Note:
            Members have intrinsic properties such as :guilabel:`CAPTION`, :guilabel:`DESCRIPTION`, or :guilabel:`MEMBER_TYPE`.
            These properties cannot be overridden through this mapping.

        Example:
            >>> populations_df = pd.DataFrame(
            ...     columns=["City", "Population"],
            ...     data=[
            ...         ("New York City", 8468000),
            ...         ("Las Vegas", 646790),
            ...         ("New Orleans", 376971),
            ...     ],
            ... )
            >>> populations_table = session.read_pandas(
            ...     populations_df, keys=["City"], table_name="Populations"
            ... )
            >>> nicknames_df = pd.DataFrame(
            ...     columns=["City name", "First", "Second"],
            ...     data=[
            ...         ("New York City", "The Big Apple", "Gotham"),
            ...         ("Las Vegas", "Sin City", "What Happens Here, Stays Here"),
            ...         ("New Orleans", "The Big Easy", None),
            ...     ],
            ... )
            >>> nicknames_table = session.read_pandas(
            ...     nicknames_df, keys=["City name"], table_name="Nicknames"
            ... )
            >>> climates_df = pd.DataFrame(
            ...     columns=["Name", "Climate"],
            ...     data=[
            ...         ("Las Vegas", "subtropical hot desert climate"),
            ...         ("New Orleans", "humid subtropical"),
            ...     ],
            ... )
            >>> climates_table = session.read_pandas(
            ...     climates_df, keys=["Name"], table_name="Climates"
            ... )
            >>> cube = session.create_cube(populations_table)
            >>> l, m = cube.levels, cube.measures
            >>> l["City"].member_properties
            {}
            >>> l["City"].member_properties.update(
            ...     {
            ...         "FIRST_ALIAS": nicknames_table["First"],
            ...         "SECOND_ALIAS": nicknames_table["Second"],
            ...         "CLIMATE": climates_table["Climate"],
            ...     }
            ... )
            >>> mdx = (
            ...     " WITH"
            ...     "   Member [Measures].[First alias]"
            ...     "     AS [Populations].[City].CurrentMember.Properties('FIRST_ALIAS')"
            ...     "   Member [Measures].[Second alias]"
            ...     "     AS [Populations].[City].CurrentMember.Properties('SECOND_ALIAS')"
            ...     "   Member [Measures].[Climate]"
            ...     "     AS [Populations].[City].CurrentMember.Properties('CLIMATE')"
            ...     " SELECT"
            ...     "   [Populations].[City].Members ON ROWS,"
            ...     "   {"
            ...     "     [Measures].[Population.SUM],"
            ...     "     [Measures].[First alias],"
            ...     "     [Measures].[Second alias],"
            ...     "     [Measures].[Climate]"
            ...     "   } ON COLUMNS"
            ...     "   FROM [Populations]"
            ... )
            >>> session.query_mdx(mdx)
                          Population.SUM    First alias                   Second alias                         Climate
            City
            Las Vegas            646,790       Sin City  What Happens Here, Stays Here  subtropical hot desert climate
            New Orleans          376,971   The Big Easy                                              humid subtropical
            New York City      8,468,000  The Big Apple                         Gotham

        """
        return MemberProperties(
            cube_name=self._cube_name,
            level_identifier=self._identifier,
            java_api=self._java_api,
        )

    @property
    def order(self) -> Order:
        """Order in which to sort the level's members.

        Defaults to ascending :class:`atoti.NaturalOrder`.
        """
        return self._java_api.get_level_order(
            self._identifier, cube_name=self._cube_name
        )

    @order.setter
    def order(self, value: Order) -> None:
        self._java_api.update_level_order(
            self._identifier,
            value,
            cube_name=self._cube_name,
        )
        self._java_api.refresh()

    @override
    def _repr_json_(self) -> ReprJson:
        data = {
            "dimension": self.dimension,
            "hierarchy": self.hierarchy,
            "type": str(self.data_type),
            "order": self.order._key,
        }
        return data, {"expanded": True, "root": self.name}
