from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

import pandas as pd
from atoti_core import Context, keyword_only_dataclass

from ._widget_conversion_details import (
    WidgetConversionDetails,
)

if TYPE_CHECKING:
    # This requires pandas' optional dependency jinja2.
    from pandas.io.formats.style import Styler  # pylint: disable=nested-import


@keyword_only_dataclass
@dataclass(frozen=True)
class QueryResultMetadata:
    context: Optional[Context]
    formatted_values: pd.DataFrame
    get_styler: Callable[[], Styler]
    initial_dataframe: pd.DataFrame
    widget_conversion_details: Optional[WidgetConversionDetails] = None
