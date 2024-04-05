from collections.abc import Collection
from typing import Protocol

from atoti_core import DataType, IdentifierT_co


class GetDataTypes(Protocol):
    def __call__(
        self, identifier: Collection[IdentifierT_co], /, *, cube_name: str
    ) -> dict[IdentifierT_co, DataType]: ...
