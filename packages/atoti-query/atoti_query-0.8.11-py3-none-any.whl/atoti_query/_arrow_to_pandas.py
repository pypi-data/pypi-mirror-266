from collections.abc import Collection

import pandas as pd
import pyarrow as pa

from ._parse_level_identifier import parse_level_identifier

# See https://arrow.apache.org/docs/python/pandas.html#nullable-types.
# Only types that can be sent by Atoti Server are listed.
_ARROW_TYPE_TO_PANDAS_NULLABLE_TYPE = {
    pa.int32(): pd.Int32Dtype(),
    pa.int64(): pd.Int64Dtype(),
    pa.bool_(): pd.BooleanDtype(),
    pa.float32(): pd.Float32Dtype(),
    pa.float64(): pd.Float64Dtype(),
    pa.string(): pd.StringDtype(),
}


def arrow_to_pandas(
    table: pa.Table,  # pyright: ignore[reportUnknownParameterType]
) -> pd.DataFrame:
    # Fast for small tables (less than 100k lines) but can take several seconds for larger datasets.
    dataframe: pd.DataFrame = table.to_pandas(
        # The level columns could stay non nullable but there is no fast way to handle them differently than measure columns.
        types_mapper=_ARROW_TYPE_TO_PANDAS_NULLABLE_TYPE.get
    )
    column_names: Collection[str] = table.column_names
    level_identifier = {
        column_name: parse_level_identifier(column_name) for column_name in column_names
    }
    return dataframe.rename(
        columns={
            column_name: level_identifier.level_name
            for column_name, level_identifier in level_identifier.items()
            if level_identifier is not None
        }
    )
