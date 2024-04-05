from __future__ import annotations

from typing import Annotated, Literal, Optional

from atoti_core import (
    PYDANTIC_CONFIG as _PYDANTIC_CONFIG,
    Condition,
    Constant,
    FrozenSequence,
    Identifiable,
    LevelIdentifier,
    MeasureIdentifier,
    keyword_only_dataclass,
)
from pydantic import Field
from pydantic.dataclasses import dataclass


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class AggregateProvider:
    """An aggregate provider pre-aggregates some table columns up to certain levels.

    If a step of a query uses a subset of the aggregate provider's levels and measures, the provider will speed up the query.

    An aggregate provider uses additional memory to store the intermediate aggregates.
    The more levels and measures are added, the more memory it requires.

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
        >>> cube.aggregate_providers.update(
        ...     {
        ...         "Seller provider": tt.AggregateProvider(
        ...             key="bitmap",
        ...             levels=[l["Seller"], l["ProductId"]],
        ...             measures=[m["Price.SUM"]],
        ...             filter=l["ProductId"] == "cdJ4",
        ...             partitioning="hash4(Seller)",
        ...         )
        ...     }
        ... )
    """

    measures: Annotated[
        FrozenSequence[Identifiable[MeasureIdentifier]],
        Field(min_length=1),
    ]
    """The measures to build the provider on."""

    key: Literal["bitmap", "leaf"] = "leaf"
    """The key of the provider.

    The bitmap is generally faster but also takes more memory.
    """

    levels: FrozenSequence[Identifiable[LevelIdentifier]] = ()
    """The levels to build the provider on."""

    filter: Optional[
        Condition[
            LevelIdentifier, Literal["eq", "isin"], Constant, Optional[Literal["and"]]
        ]
    ] = None
    """Only compute and provide aggregates matching this condition.

    The levels used in the condition do not have to be part of this provider's *levels*.
    """

    partitioning: Optional[str] = None
    """The partitioning of the provider.

    Default to the partitioning of the cube's base table.
    """
