from dataclasses import dataclass

from atoti_core import keyword_only_dataclass


@keyword_only_dataclass
@dataclass(frozen=True)
class ExternalAggregateTableSql:
    create: str
    insert: str
