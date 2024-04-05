from typing import Literal, Optional

from atoti_core import (
    PYDANTIC_CONFIG,
    ColumnIdentifier,
    Condition,
    ConditionCombinationOperatorBound,
    Constant,
    Identifiable,
    TableIdentifier,
    keyword_only_dataclass,
)
from pydantic.dataclasses import dataclass

TableUpdateChangeType = Literal["add", "remove", "update", "mixed", "infer"]

TableUpdatePerimeter = Condition[
    ColumnIdentifier,
    Literal["eq", "isin", "ne"],
    Constant,
    ConditionCombinationOperatorBound,
]


@keyword_only_dataclass
@dataclass(config=PYDANTIC_CONFIG, frozen=True)
class TableUpdate:
    """The description of an update that occurred on an external table.

    It is used to compute the smallest incremental refresh possible.
    """

    table: Identifiable[TableIdentifier]
    """The table on which the update occurred."""

    change_type: TableUpdateChangeType = "mixed"
    """The type of change that occurred:

    * ``"add"``: Some rows have been added.
    * ``"update"``: Some rows have been updated (e.g. the values of some non key columns changed).
      The updated columns cannot be used in *perimeter*.
    * ``"remove"``: Some rows have been removed.
    * ``"mixed"``: Some rows have been added, updated, or removed.
      If updated columns are used in *perimeter*, the condition must cover both previous and new values.
    * ``"infer"``: Some rows have been added to this *table* and the one it is joined to (declared in another ``TableUpdate``).
      This can be used when *table* is the target of a :meth:`~atoti.Table.join` created with ``target_optionality="mandatory"``.
      When that is the case, the added rows on this target *table* can be inferred from the *perimeter* of the ``TableUpdate`` (with *change_type* set to ``"add"``) of the source table.
      The row location information for this *table* is thus not required to perform an efficient incremental refresh.

    """

    perimeter: Optional[TableUpdatePerimeter] = None
    """The condition describing the perimeter of the changed rows.

    * If ``None`` and *change_type* is different than ``"infer"`, all rows are considered to have changed.
    * If not ``None``, the condition must evaluate to ``True`` for all the changed rows and to ``False`` everywhere else.
    """

    def __post_init__(self) -> None:
        if self.change_type == "infer" and self.perimeter is not None:
            raise ValueError(
                "Cannot specify a perimeter when inferring the change type."
            )
