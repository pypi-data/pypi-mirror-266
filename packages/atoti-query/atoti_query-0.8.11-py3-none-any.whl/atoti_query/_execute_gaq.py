from collections.abc import Collection
from datetime import timedelta
from typing import Optional, Protocol

import pandas as pd
from atoti_core import LevelIdentifier, MeasureIdentifier

from ._gaq_filter import GaqFilter


class ExecuteGaq(Protocol):
    def __call__(
        self,
        *,
        cube_name: str,
        filter: Optional[GaqFilter] = None,  # noqa: A002
        include_empty_rows: bool,
        include_totals: bool,
        level_identifiers: Collection[LevelIdentifier],
        measure_identifiers: Collection[MeasureIdentifier],
        scenario: str,
        timeout: timedelta,
    ) -> pd.DataFrame: ...
