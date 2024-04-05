from __future__ import annotations

from collections.abc import (
    Callable,
    Collection,
    Mapping,
    MutableMapping,
    Sequence,
)
from typing import (
    Annotated,
    Any,
    Optional,
    Protocol,
)

import pandas as pd
from atoti_core import (
    BASE_SCENARIO_NAME as _BASE_SCENARIO_NAME,
    DEPRECATED_WARNING_CATEGORY,
    ActiveViamClient,
    Constant,
    ConstantValue,
    DataType,
    HierarchyIdentifier,
    Identifier,
    IdentifierT_co,
    LevelIdentifier,
    MeasureIdentifier,
    Plugin,
    SequenceOrDeprecatedSet,
    TableIdentifier,
    frozendict,
    is_temporal_type,
)
from atoti_query import QuerySession
from pydantic import Field
from typing_extensions import deprecated, override

from ._aggregate_providers import AggregateProviders
from ._hierarchy_arguments import HierarchyArguments
from ._java_api import JavaApi
from ._local_cube import LocalCube
from ._shared_context import SharedContext
from .agg import single_value
from .aggregate_provider import AggregateProvider
from .aggregates_cache import AggregatesCache
from .column import Column
from .hierarchies import Hierarchies
from .hierarchy import Hierarchy
from .level import Level
from .levels import Levels
from .measures import Measures
from .table import Table, _LoadKafka, _LoadSql


class _ReadPandas(Protocol):
    def __call__(
        self,
        dataframe: pd.DataFrame,
        /,
        *,
        table_name: str,
        keys: Sequence[str] = (),
        partitioning: Optional[str] = None,
        types: Mapping[str, DataType] = frozendict(),
        **kwargs: Any,
    ) -> Table: ...


_DEFAULT_DATE_HIERARCHY_LEVELS = frozendict({"Year": "y", "Month": "M", "Day": "d"})


class Cube(LocalCube[Hierarchies, Levels, Measures]):
    """Cube of a :class:`~atoti.Session`."""

    def __init__(
        self,
        name: str,
        /,
        *,
        base_table: Table,
        client: ActiveViamClient,
        create_query_session: Callable[[], QuerySession],
        get_schema: Callable[[], object],
        java_api: JavaApi,
        load_kafka: _LoadKafka,
        load_sql: _LoadSql,
        plugins: Mapping[str, Plugin],
        read_pandas: _ReadPandas,
        session_name: Optional[str],
    ):
        super().__init__(
            name,
            aggregates_cache=AggregatesCache(
                cube_name=name,
                get_capacity=java_api.get_aggregates_cache_capacity,
                set_capacity=java_api.set_aggregates_cache_capacity,
            ),
            client=client,
            create_query_session=create_query_session,
            hierarchies=Hierarchies(
                create_hierarchy_from_arguments=self._create_hierarchy_from_arguments,
                cube_name=name,
                java_api=java_api,
            ),
            java_api=java_api,
            level_function=lambda hierarchies: Levels(hierarchies=hierarchies),
            measures=Measures(java_api=java_api, cube_name=name),
            session_name=session_name,
        )

        self._base_table = base_table
        self._get_schema = get_schema
        self._load_kafka = load_kafka
        self._load_sql = load_sql
        self._plugins = plugins
        self._read_pandas = read_pandas

    @property
    @deprecated(
        "Accessing the database sub schema for a specific cube is deprecated. Use `Session.tables.schema` instead",
        category=DEPRECATED_WARNING_CATEGORY,
    )
    def schema(self) -> object:
        """Schema of the cube's tables, as an SVG image in IPython, as a path to the image otherwise.

        :meta private:
        """
        return self._get_schema()

    @property
    def shared_context(self) -> MutableMapping[str, str]:
        """Context values shared by all the users.

        Context values can also be set at query time, and per user, directly from the UI.
        The values in the shared context are the default ones for all the users.

        * ``queriesTimeLimit``

          The number of seconds after which a running query is cancelled and its resources reclaimed.
          Set to ``-1`` to remove the limit.
          Defaults to 30 seconds.

        * ``queriesResultLimit.intermediateLimit``

          The limit number of point locations for a single intermediate result.
          This works as a safe-guard to prevent queries from consuming too much memory, which is especially useful when going to production with several simultaneous users on the same server.
          Set to ``-1`` to remove the limit.

          Defaults to ``1_000_000`` if `ATOTI_LICENSE is set  <../../how_tos/unlock_all_features.html>`__, and to no limit otherwise.

        * ``queriesResultLimit.transientLimit``

          Similar to *intermediateLimit* but across all the intermediate results of the same query.
          Set to ``-1`` to remove the limit.

          Defaults to ``10_000_000`` if `ATOTI_LICENSE is set  <../../how_tos/unlock_all_features.html>`__, and to no limit otherwise.

        Example:
            >>> df = pd.DataFrame(
            ...     columns=["City", "Price"],
            ...     data=[
            ...         ("London", 240.0),
            ...         ("New York", 270.0),
            ...         ("Paris", 200.0),
            ...     ],
            ... )
            >>> table = session.read_pandas(
            ...     df, keys=["City"], table_name="shared_context example"
            ... )
            >>> cube = session.create_cube(table)
            >>> cube.shared_context["queriesTimeLimit"] = 60
            >>> cube.shared_context["queriesResultLimit.intermediateLimit"] = 1000000
            >>> cube.shared_context["queriesResultLimit.transientLimit"] = 10000000
            >>> cube.shared_context
            {'queriesTimeLimit': '60', 'queriesResultLimit.transientLimit': '10000000', 'queriesResultLimit.intermediateLimit': '1000000'}

        """
        return SharedContext(cube_name=self.name, java_api=self._java_api)

    @property
    def aggregate_providers(self) -> MutableMapping[str, AggregateProvider]:
        return AggregateProviders(cube_name=self.name, java_api=self._java_api)

    def _join_distributed_cluster(
        self,
        *,
        query_cube_name: str,
        query_cube_url: str,
        query_cube_port: Optional[int],
        data_cube_url: Optional[str],
        data_cube_port: Optional[int],
        discovery_protocol_xml: Optional[str],
    ) -> None:
        """Join the distributed cluster at the given address for the given distributed cube."""
        self._java_api.join_distributed_cluster(
            query_cube_name=query_cube_name,
            query_cube_url=query_cube_url,
            query_cube_port=query_cube_port,
            data_cube_name=self.name,
            data_cube_url=data_cube_url,
            data_cube_port=data_cube_port,
            discovery_protocol_xml=discovery_protocol_xml,
        )
        self._java_api.refresh()

    @override
    def _get_data_types(
        self, identifiers: Collection[IdentifierT_co], /
    ) -> dict[IdentifierT_co, DataType]:
        def get_data_type(identifier: Identifier, /) -> DataType:
            if isinstance(identifier, LevelIdentifier):
                return (
                    "String"
                    if identifier
                    == LevelIdentifier(HierarchyIdentifier("Epoch", "Epoch"), "Branch")
                    else self.levels[identifier.key].data_type
                )

            assert isinstance(identifier, MeasureIdentifier)
            measure = self.measures.get(identifier.measure_name)
            # The passed identifier can be the ones of a calculated measure for which the type is unknown.
            return "Object" if measure is None else measure.data_type

        return {identifier: get_data_type(identifier) for identifier in identifiers}

    def create_parameter_simulation(
        self,
        name: str,
        *,
        measures: Annotated[
            Mapping[str, Optional[ConstantValue]],
            Field(min_length=1),
        ],
        levels: SequenceOrDeprecatedSet[Level] = (),
        base_scenario_name: str = _BASE_SCENARIO_NAME,
    ) -> Table:
        """Create a parameter simulation and its associated measures.

        Args:
            name: The name of the simulation.
              This is also the name of the corresponding table that will be created.
            measures: The mapping from the names of the created measures to their default value.
            levels: The levels to simulate on.
            base_scenario_name: The name of the base scenario.

        Example:
            >>> sales_table = session.read_csv(
            ...     f"{TUTORIAL_RESOURCES}/sales.csv",
            ...     table_name="Sales",
            ...     keys=["Sale ID"],
            ... )
            >>> shops_table = session.read_csv(
            ...     f"{TUTORIAL_RESOURCES}/shops.csv",
            ...     table_name="Shops",
            ...     keys=["Shop ID"],
            ... )
            >>> sales_table.join(shops_table, sales_table["Shop"] == shops_table["Shop ID"])
            >>> cube = session.create_cube(sales_table)
            >>> l, m = cube.levels, cube.measures

            Creating a parameter simulation on one level:

            >>> country_simulation = cube.create_parameter_simulation(
            ...     "Country simulation",
            ...     measures={"Country parameter": 1.0},
            ...     levels=[l["Country"]],
            ... )
            >>> country_simulation += ("France crash", "France", 0.8)
            >>> country_simulation.head()
                                  Country parameter
            Scenario     Country
            France crash France                 0.8

            * ``France crash`` is the name of the scenario.
            * ``France`` is the coordinate at which the value will be changed.
            * ``0.8`` is the value the :guilabel:`Country parameter` measure will have in this scenario.

            >>> m["Unparametrized turnover"] = tt.agg.sum(
            ...     sales_table["Unit price"] * sales_table["Quantity"]
            ... )
            >>> m["Turnover"] = tt.agg.sum(
            ...     m["Unparametrized turnover"] * m["Country parameter"],
            ...     scope=tt.OriginScope(levels={l["Country"]}),
            ... )
            >>> cube.query(m["Turnover"], levels=[l["Country simulation"]])
                                  Turnover
            Country simulation
            Base                961,463.00
            France crash        889,854.60

            Drilldown to the :guilabel:`Country` level for more details:

            >>> cube.query(
            ...     m["Unparametrized turnover"],
            ...     m["Country parameter"],
            ...     m["Turnover"],
            ...     levels=[l["Country simulation"], l["Country"]],
            ... )
                                       Unparametrized turnover Country parameter    Turnover
            Country simulation Country
            Base               France               358,042.00              1.00  358,042.00
                               USA                  603,421.00              1.00  603,421.00
            France crash       France               358,042.00               .80  286,433.60
                               USA                  603,421.00              1.00  603,421.00

            Creating a parameter simulation on multiple levels:

            >>> size_simulation = cube.create_parameter_simulation(
            ...     "Size simulation",
            ...     measures={"Size parameter": 1.0},
            ...     levels=[l["Country"], l["Shop size"]],
            ... )
            >>> size_simulation += (
            ...     "Going local",
            ...     None,  # ``None`` serves as a wildcard matching any member value.
            ...     "big",
            ...     0.8,
            ... )
            >>> size_simulation += ("Going local", "USA", "small", 1.2)
            >>> m["Turnover"] = tt.agg.sum(
            ...     m["Unparametrized turnover"]
            ...     * m["Country parameter"]
            ...     * m["Size parameter"],
            ...     scope=tt.OriginScope(levels={l["Country"], l["Shop size"]}),
            ... )
            >>> cube.query(
            ...     m["Turnover"],
            ...     levels=[l["Size simulation"], l["Shop size"]],
            ... )
                                         Turnover
            Size simulation Shop size
            Base            big        120,202.00
                            medium     356,779.00
                            small      484,482.00
            Going local     big         96,161.60
                            medium     356,779.00
                            small      547,725.20

            When several rules contain ``None``, the one where the first ``None`` appears last takes precedence.

            >>> size_simulation += ("Going France and Local", "France", None, 2)
            >>> size_simulation += ("Going France and Local", None, "small", 10)
            >>> cube.query(
            ...     m["Unparametrized turnover"],
            ...     m["Turnover"],
            ...     levels=[l["Country"], l["Shop size"]],
            ...     filter=l["Size simulation"] == "Going France and Local",
            ... )
                              Unparametrized turnover      Turnover
            Country Shop size
            France  big                     47,362.00     94,724.00
                    medium                 142,414.00    284,828.00
                    small                  168,266.00    336,532.00
            USA     big                     72,840.00     72,840.00
                    medium                 214,365.00    214,365.00
                    small                  316,216.00  3,162,160.00

            Creating a parameter simulation without levels:

            >>> crisis_simulation = cube.create_parameter_simulation(
            ...     "Global Simulation",
            ...     measures={"Global parameter": 1.0},
            ... )
            >>> crisis_simulation += ("Global Crisis", 0.9)
            >>> m["Turnover"] = m["Unparametrized turnover"] * m["Global parameter"]
            >>> cube.query(m["Turnover"], levels=[l["Global Simulation"]])
                                 Turnover
            Global Simulation
            Base               961,463.00
            Global Crisis      865,316.70

            Creating a parameter simulation with multiple measures:

            >>> multi_parameter_simulation = cube.create_parameter_simulation(
            ...     "Price And Quantity",
            ...     measures={
            ...         "Price parameter": 1.0,
            ...         "Quantity parameter": 1.0,
            ...     },
            ... )
            >>> multi_parameter_simulation += ("Price Up Quantity Down", 1.2, 0.8)
            >>> m["Simulated Price"] = (
            ...     tt.agg.single_value(sales_table["Unit price"]) * m["Price parameter"]
            ... )
            >>> m["Simulated Quantity"] = (
            ...     tt.agg.single_value(sales_table["Quantity"]) * m["Quantity parameter"]
            ... )
            >>> m["Turnover"] = tt.agg.sum_product(
            ...     m["Simulated Price"],
            ...     m["Simulated Quantity"],
            ...     scope=tt.OriginScope(levels={l["Sale ID"]}),
            ... )
            >>> cube.query(m["Turnover"], levels=[l["Price And Quantity"]])
                                      Turnover
            Price And Quantity
            Base                    961,463.00
            Price Up Quantity Down  923,004.48

        """
        if any(level.name == "Scenario" for level in levels):
            raise ValueError(
                'Levels with the name "Scenario" cannot be used in parameter simulations.'
            )

        self._java_api.create_parameter_simulation(
            cube_name=self.name,
            simulation_name=name,
            level_identifiers=[level._identifier for level in levels],
            base_scenario_name=base_scenario_name,
            measures={
                MeasureIdentifier(measure_name): None
                if default_value is None
                else Constant(default_value)
                for measure_name, default_value in measures.items()
            },
        )
        return Table(
            TableIdentifier(name),
            client=self._client,
            java_api=self._java_api,
            load_kafka=self._load_kafka,
            load_sql=self._load_sql,
            plugins=self._plugins,
        )

    def create_parameter_hierarchy_from_column(self, name: str, column: Column) -> None:
        """Create a single-level hierarchy which dynamically takes its members from a column.

        Args:
            name: Name given to the created dimension, hierarchy and its single level.
            column: Column from which to take members.

        Example:
            >>> df = pd.DataFrame(
            ...     {
            ...         "Seller": ["Seller_1", "Seller_1", "Seller_2", "Seller_2"],
            ...         "ProductId": ["aBk3", "ceJ4", "aBk3", "ceJ4"],
            ...         "Price": [2.5, 49.99, 3.0, 54.99],
            ...     }
            ... )
            >>> table = session.read_pandas(df, table_name="Seller")
            >>> cube = session.create_cube(table)
            >>> l, m = cube.levels, cube.measures
            >>> cube.create_parameter_hierarchy_from_column("Competitor", table["Seller"])
            >>> m["Price"] = tt.agg.single_value(table["Price"])
            >>> m["Competitor price"] = tt.at(m["Price"], l["Seller"] == l["Competitor"])
            >>> cube.query(
            ...     m["Competitor price"],
            ...     levels=[l["Seller"], l["ProductId"]],
            ... )
                               Competitor price
            Seller   ProductId
            Seller_1 aBk3                  2.50
                     ceJ4                 49.99
            Seller_2 aBk3                  2.50
                     ceJ4                 49.99
            >>> cube.query(
            ...     m["Competitor price"],
            ...     levels=[l["Seller"], l["ProductId"]],
            ...     filter=l["Competitor"] == "Seller_2",
            ... )
                               Competitor price
            Seller   ProductId
            Seller_1 aBk3                  3.00
                     ceJ4                 54.99
            Seller_2 aBk3                  3.00
                     ceJ4                 54.99
        """
        self._java_api.create_analysis_hierarchy(
            name,
            column_identifier=column._identifier,
            cube_name=self.name,
        )
        self._java_api.refresh()

    def create_parameter_hierarchy_from_members(
        self,
        name: str,
        members: SequenceOrDeprecatedSet[ConstantValue],
        *,
        data_type: Optional[DataType] = None,
        index_measure_name: Optional[str] = None,
    ) -> None:
        """Create a single-level hierarchy with the given members.

        It can be used as a parameter hierarchy in advanced analyzes.

        Args:
            name: The name of hierarchy and its single level.
            members: The members of the hierarchy.
            data_type: The type with which the members will be stored.
                Automatically inferred by default.
            index_measure_name: The name of the indexing measure to create for this hierarchy, if any.

        Example:
            >>> df = pd.DataFrame(
            ...     {
            ...         "Seller": ["Seller_1", "Seller_2", "Seller_3"],
            ...         "Prices": [
            ...             [2.5, 49.99, 3.0, 54.99],
            ...             [2.6, 50.99, 2.8, 57.99],
            ...             [2.99, 44.99, 3.6, 59.99],
            ...         ],
            ...     }
            ... )
            >>> table = session.read_pandas(df, table_name="Seller prices")
            >>> cube = session.create_cube(table)
            >>> l, m = cube.levels, cube.measures
            >>> cube.create_parameter_hierarchy_from_members(
            ...     "ProductID",
            ...     ["aBk3", "ceJ4", "aBk5", "ceJ9"],
            ...     index_measure_name="Product index",
            ... )
            >>> m["Prices"] = tt.agg.single_value(table["Prices"])
            >>> m["Product price"] = m["Prices"][m["Product index"]]
            >>> cube.query(
            ...     m["Product price"],
            ...     levels=[l["Seller"], l["ProductID"]],
            ... )
                               Product price
            Seller   ProductID
            Seller_1 aBk3               2.50
                     aBk5               3.00
                     ceJ4              49.99
                     ceJ9              54.99
            Seller_2 aBk3               2.60
                     aBk5               2.80
                     ceJ4              50.99
                     ceJ9              57.99
            Seller_3 aBk3               2.99
                     aBk5               3.60
                     ceJ4              44.99
                     ceJ9              59.99

        """
        index_column = f"{name} index"
        parameter_df = pd.DataFrame({name: members})
        types: dict[str, DataType] = {}
        if index_measure_name is not None:
            parameter_df[index_column] = list(range(len(members)))
            types[index_column] = "int"

        if data_type:
            types[name] = data_type
        elif all(
            isinstance(member, int) and -(2**31) <= member < 2**31 for member in members
        ):
            types[name] = "int"

        parameter_table = self._read_pandas(
            parameter_df,
            table_name=name,
            keys=[name],
            types=types,
            is_parameter_table=True,
        )

        self._java_api.create_join(
            self._base_table._identifier,
            parameter_table._identifier,
            mapping={},
            target_optionality="optional",
        )

        if index_measure_name is not None:
            self.measures[index_measure_name] = single_value(
                parameter_table[index_column]
            )

        self.hierarchies[name, name].slicing = True

        self._java_api.refresh()

    def create_date_hierarchy(
        self,
        name: str,
        *,
        column: Column,
        levels: Mapping[str, str] = _DEFAULT_DATE_HIERARCHY_LEVELS,
    ) -> None:
        """Create a multilevel date hierarchy based on a date column.

        The new levels are created by matching a `date pattern <https://docs.oracle.com/en/java/javase/15/docs/api/java.base/java/time/format/DateTimeFormatter.html#patterns>`_.
        Here is a non-exhaustive list of patterns that can be used:

        +---------+-----------------------------+---------+-----------------------------------+
        | Pattern | Description                 | Type    | Examples                          |
        +=========+=============================+=========+===================================+
        | y       | Year                        | Integer | ``2001, 2005, 2020``              |
        +---------+-----------------------------+---------+-----------------------------------+
        | yyyy    | 4-digits year               | String  | ``"2001", "2005", "2020"``        |
        +---------+-----------------------------+---------+-----------------------------------+
        | M       | Month of the year (1 based) | Integer | ``1, 5, 12``                      |
        +---------+-----------------------------+---------+-----------------------------------+
        | MM      | 2-digits month              | String  | ``"01", "05", "12"``              |
        +---------+-----------------------------+---------+-----------------------------------+
        | d       | Day of the month            | Integer | ``1, 15, 30``                     |
        +---------+-----------------------------+---------+-----------------------------------+
        | dd      | 2-digits day of the month   | String  | ``"01", "15", "30"``              |
        +---------+-----------------------------+---------+-----------------------------------+
        | w       | Week number                 | Integer | ``1, 12, 51``                     |
        +---------+-----------------------------+---------+-----------------------------------+
        | Q       | Quarter                     | Integer | ``1, 2, 3, 4``                    |
        +---------+-----------------------------+---------+-----------------------------------+
        | QQQ     | Quarter prefixed with Q     | String  | ``"Q1", "Q2", "Q3", "Q4"``        |
        +---------+-----------------------------+---------+-----------------------------------+
        | H       | Hour of day (0-23)          | Integer | ``0, 12, 23``                     |
        +---------+-----------------------------+---------+-----------------------------------+
        | HH      | 2-digits hour of day        | String  | ``"00", "12", "23"``              |
        +---------+-----------------------------+---------+-----------------------------------+
        | m       | Minute of hour              | Integer | ``0, 30, 59``                     |
        +---------+-----------------------------+---------+-----------------------------------+
        | mm      | 2-digits minute of hour     | String  | ``"00", "30", "59"``              |
        +---------+-----------------------------+---------+-----------------------------------+
        | s       | Second of minute            | Integer | ``0, 5, 55``                      |
        +---------+-----------------------------+---------+-----------------------------------+
        | ss      | 2-digits second of minute   | String  | ``"00", "05", "55"``              |
        +---------+-----------------------------+---------+-----------------------------------+

        Args:
            name: The name of the hierarchy to create.
            column: A table column containing a date or a datetime.
            levels: The mapping from the names of the levels to the patterns from which they will be created.

        Example:
            >>> from datetime import date
            >>> df = pd.DataFrame(
            ...     columns=["Date", "Quantity"],
            ...     data=[
            ...         (date(2020, 1, 10), 150.0),
            ...         (date(2020, 1, 20), 240.0),
            ...         (date(2019, 3, 17), 270.0),
            ...         (date(2019, 12, 12), 200.0),
            ...     ],
            ... )
            >>> table = session.read_pandas(
            ...     df, keys=["Date"], table_name="create_date_hierarchy example"
            ... )
            >>> cube = session.create_cube(table)
            >>> l, m = cube.levels, cube.measures
            >>> cube.create_date_hierarchy("Date parts", column=table["Date"])
            >>> cube.query(
            ...     m["Quantity.SUM"],
            ...     include_totals=True,
            ...     levels=[l["Year"], l["Month"], l["Day"]],
            ... )
                            Quantity.SUM
            Year  Month Day
            Total                 860.00
            2019                  470.00
                  3               270.00
                        17        270.00
                  12              200.00
                        12        200.00
            2020                  390.00
                  1               390.00
                        10        150.00
                        20        240.00

            The full date can also be added back as the last level of the hierarchy:

            >>> h = cube.hierarchies
            >>> h["Date parts"] = {**h["Date parts"].levels, "Date": table["Date"]}
            >>> cube.query(
            ...     m["Quantity.SUM"],
            ...     include_totals=True,
            ...     levels=[l["Date parts", "Date"]],
            ... )
                                       Quantity.SUM
            Year  Month Day Date
            Total                            860.00
            2019                             470.00
                  3                          270.00
                        17                   270.00
                            2019-03-17       270.00
                  12                         200.00
                        12                   200.00
                            2019-12-12       200.00
            2020                             390.00
                  1                          390.00
                        10                   150.00
                            2020-01-10       150.00
                        20                   240.00
                            2020-01-20       240.00

            Data inserted into the table after the hierarchy creation will be automatically hierarchized:

            >>> table += (date(2021, 8, 30), 180.0)
            >>> cube.query(
            ...     m["Quantity.SUM"],
            ...     include_totals=True,
            ...     levels=[l["Date parts", "Date"]],
            ...     filter=l["Year"] == "2021",
            ... )
                                       Quantity.SUM
            Year  Month Day Date
            Total                            180.00
            2021                             180.00
                  8                          180.00
                        30                   180.00
                            2021-08-30       180.00

        """
        if not is_temporal_type(column.data_type):
            raise ValueError(
                f"Cannot create a date hierarchy from a column which is not temporal, column `{column.name}` is of type `{column.data_type}`."
            )
        self._java_api.create_date_hierarchy(
            name,
            cube_name=self.name,
            column_identifier=column._identifier,
            levels=levels,
        )
        self._java_api.refresh()

    @override
    def _create_hierarchy_from_arguments(
        self, arguments: HierarchyArguments
    ) -> Hierarchy:
        return Hierarchy(
            arguments.identifier,
            cube_name=self.name,
            java_api=self._java_api,
            levels_arguments=arguments.levels_arguments,
            slicing=arguments.slicing,
            virtual=arguments.virtual,
            visible=arguments.visible,
            dimension_default=arguments.dimension_default,
        )
