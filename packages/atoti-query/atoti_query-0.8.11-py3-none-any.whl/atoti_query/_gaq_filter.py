from __future__ import annotations

from typing import Literal, Optional

from atoti_core import Condition, Constant, LevelIdentifier

GaqFilter = Condition[
    LevelIdentifier,
    Literal["eq", "isin", "ne"],
    Constant,
    Optional[Literal["and"]],
]
