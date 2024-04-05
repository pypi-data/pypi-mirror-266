from typing import Optional

from atoti_core import PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic import SkipValidation
from pydantic.dataclasses import dataclass

from ._get_data_types import GetDataTypes


@keyword_only_dataclass
@dataclass(config=PYDANTIC_CONFIG, frozen=True)
class QueryPrivateParameters:
    get_data_types: Optional[SkipValidation[GetDataTypes]] = None
