from collections.abc import Collection

from atoti_core import (
    ComparisonOperator,
    Constant,
    LevelIdentifier,
    QueryFilter,
    decombine_condition,
)
from typing_extensions import TypeGuard

from ._gaq_filter import GaqFilter

_SUPPORTED_COMPARISON_OPERATORS: Collection[ComparisonOperator] = frozenset(
    {"eq", "ne"}
)
_SUPPORTED_TARGET_TYPES = (int, float, str)


def is_gaq_filter(
    filter: QueryFilter,  # noqa: A002
    /,
) -> TypeGuard[GaqFilter]:
    comparison_conditions, level_isin_conditions, hierarchy_isin_conditions = (
        decombine_condition(  # type: ignore[var-annotated]
            filter,
            allowed_subject_types=(LevelIdentifier,),
            allowed_combination_operators=("and",),
            allowed_target_types=(Constant,),
        )[0]
    )
    return (
        all(
            condition.operator in _SUPPORTED_COMPARISON_OPERATORS
            and isinstance(condition.target.value, _SUPPORTED_TARGET_TYPES)
            for condition in comparison_conditions
        )
        and all(
            element is not None and isinstance(element.value, _SUPPORTED_TARGET_TYPES)
            for condition in level_isin_conditions
            for element in condition.elements
        )
        and not hierarchy_isin_conditions
    )
