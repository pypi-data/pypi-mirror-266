from typing import Any

from ..enums.join_type_enum import JoinType


def inner_join(target) -> tuple[Any, int]:
    return target, JoinType.INNER_JOIN


def left_join(target) -> tuple[Any, int]:
    return target, JoinType.LEFT_JOIN
