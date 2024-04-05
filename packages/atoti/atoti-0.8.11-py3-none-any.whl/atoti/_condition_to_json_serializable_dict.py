from typing import Union

from atoti_core import (
    ColumnIdentifier,
    Condition,
    ConditionCombinationOperatorBound,
    ConditionComparisonOperatorBound,
    Constant,
    ConstantJson,
    decombine_condition,
)

_AndDict = dict[str, dict[str, Union[ConstantJson, list[ConstantJson]]]]

_OrDict = dict[str, list[_AndDict]]

_JsonSerializableDict = dict[str, list[_OrDict]]


def condition_to_json_serializable_dict(
    condition: Condition[
        ColumnIdentifier,
        ConditionComparisonOperatorBound,
        Constant,
        ConditionCombinationOperatorBound,
    ],
) -> _JsonSerializableDict:
    or_dicts: list[_OrDict] = []

    for or_condition in decombine_condition(  # type: ignore[var-annotated]
        condition,
        allowed_isin_element_types=(Constant,),
        allowed_subject_types=(ColumnIdentifier,),
        allowed_target_types=(Constant,),
    ):
        and_list: list[_AndDict] = []
        comparison_conditions, isin_conditions, *_ = or_condition

        for comparison_condition in comparison_conditions:
            column_name = comparison_condition.subject.column_name

            if comparison_condition.operator == "ne":
                and_list.append(
                    {"$not": {column_name: comparison_condition.target.json}}
                )
            else:
                operator = (
                    "lte"
                    if comparison_condition.operator == "le"
                    else "gte"
                    if comparison_condition.operator == "ge"
                    else comparison_condition.operator
                )
                and_list.append(
                    {column_name: {f"${operator}": comparison_condition.target.json}}
                )

        and_list.extend(
            {
                isin_condition.subject.column_name: {
                    "$in": [element.json for element in isin_condition.elements]
                }
            }
            for isin_condition in isin_conditions
        )

        or_dicts.append({"$and": and_list})

    return {"$or": or_dicts}
