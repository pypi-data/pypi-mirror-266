from datetime import timedelta
from typing import Any, Literal, Protocol

import pandas as pd
from atoti_core import DEFAULT_QUERY_TIMEOUT, Context, frozendict


class QueryMdx(Protocol):
    def __call__(
        self,
        mdx: str,
        *,
        context: Context = frozendict(),
        keep_totals: bool = False,
        mode: Literal["pretty", "raw"] = "pretty",
        timeout: timedelta = DEFAULT_QUERY_TIMEOUT,
        **kwargs: Any,
    ) -> pd.DataFrame: ...
