from atoti_core import (
    PYDANTIC_CONFIG as _PYDANTIC_CONFIG,
    SetOrDeprecatedSequence,
    keyword_only_dataclass,
)
from pydantic.dataclasses import dataclass


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class MultiColumnArrayConversion:
    """Convert an external table where array values are stored with one element per column to a table with array columns.

    Groups of a least 2 columns named as ``"f{prefix}_{index}"`` (indices being consecutive and starting with 0 or 1) can be converted into array columns.

    Example:
        .. doctest:: MultiColumnArrayConversion
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

        .. doctest:: MultiColumnArrayConversion

            >>> external_database = session.connect_to_external_database(connection_info)
            >>> external_table = external_database.tables["TUTORIAL", "MULTI_COLUMN_QUANTITY"]

        ``external_table`` has 5 :guilabel:`QUANTITY_{index}` columns:

        .. doctest:: MultiColumnArrayConversion

            >>> external_table.columns
            ['PRODUCT', 'QUANTITY_0', 'QUANTITY_1', 'QUANTITY_2', 'QUANTITY_3', 'QUANTITY_4']

        and its content is:

        +-----------+------------+------------+------------+------------+------------+
        |  PRODUCT  | QUANTITY_0 | QUANTITY_1 | QUANTITY_2 | QUANTITY_3 | QUANTITY_4 |
        +===========+============+============+============+============+============+
        | product_1 |       10.0 |       20.0 |       15.0 |       25.0 |       10.0 |
        +-----------+------------+------------+------------+------------+------------+
        | product_2 |       50.0 |       65.0 |       55.0 |       30.0 |       80.0 |
        +-----------+------------+------------+------------+------------+------------+

        It can be converted into a table with an array column:

        .. doctest:: MultiColumnArrayConversion

            >>> from atoti_directquery_snowflake import SnowflakeTableOptions
            >>> table = session.add_external_table(
            ...     external_table,
            ...     table_name="Sales (Multi column array)",
            ...     options=SnowflakeTableOptions(
            ...         keys=["PRODUCT"],
            ...         array_conversion=tt.MultiColumnArrayConversion(
            ...             column_prefixes={"QUANTITY"},
            ...         ),
            ...     ),
            ... )
            >>> table.head().sort_index()
                                             QUANTITY
            PRODUCT
            product_1  [10.0, 20.0, 15.0, 25.0, 10.0]
            product_2  [50.0, 65.0, 55.0, 30.0, 80.0]

    See Also:
        :class:`~atoti.AutoMultiColumnArrayConversion`
    """

    column_prefixes: SetOrDeprecatedSequence[str]
    """
    The prefixes of the array element columns in the external table.

    One array column per prefix will be created.
    """
