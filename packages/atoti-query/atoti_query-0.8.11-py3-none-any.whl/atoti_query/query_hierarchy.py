from collections.abc import Mapping

from atoti_core import BaseHierarchy, HierarchyIdentifier
from typing_extensions import override

from .query_level import QueryLevel


class QueryHierarchy(BaseHierarchy[QueryLevel]):
    def __init__(
        self,
        identifier: HierarchyIdentifier,
        /,
        *,
        levels: Mapping[str, QueryLevel],
        slicing: bool,
    ) -> None:
        super().__init__(identifier)

        self._levels = levels
        self._slicing = slicing

    @property
    @override
    def levels(self) -> Mapping[str, QueryLevel]:
        """Levels of the hierarchy."""
        return self._levels

    @property
    @override
    def slicing(self) -> bool:
        """Whether the hierarchy is slicing or not."""
        return self._slicing
