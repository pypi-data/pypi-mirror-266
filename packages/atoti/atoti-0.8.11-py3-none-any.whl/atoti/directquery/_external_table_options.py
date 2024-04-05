from collections.abc import Set as AbstractSet
from typing import Generic, Optional, Union

from atoti_core import (
    PYDANTIC_CONFIG as _PYDANTIC_CONFIG,
    FrozenSequence,
    SetOrDeprecatedSequence,
    keyword_only_dataclass,
)
from pydantic.dataclasses import dataclass

from ._external_table import ExternalTableT_co


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class ExternalTableOptions(Generic[ExternalTableT_co]):
    clustering_columns: SetOrDeprecatedSequence[str] = frozenset()
    """The names of the columns used for clustering.

    Feeding aggregate providers from an external database can result in very large queries to be run on this database.
    Clustering columns split up queries made by DirectQuery to the external database when feeding aggregate providers.
    """

    keys: Optional[Union[FrozenSequence[str], AbstractSet[str]]] = None
    """The columns that will become the table :attr:`~atoti.Table.keys`."""
