from __future__ import annotations

from typing import Literal, Optional

from atoti_core import ColumnIdentifier, Condition, Constant

Restriction = Condition[
    ColumnIdentifier,
    Literal["eq", "isin"],
    Constant,
    Optional[Literal["and"]],
]
