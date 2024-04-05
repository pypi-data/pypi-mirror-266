from __future__ import annotations

from atoti_core import BaseLevel, ReprJson
from typing_extensions import override


class QueryLevel(BaseLevel):
    @override
    def _repr_json_(self) -> ReprJson:
        data = {
            "dimension": self.dimension,
            "hierarchy": self.hierarchy,
        }
        return (
            data,
            {"expanded": True, "root": self.name},
        )
