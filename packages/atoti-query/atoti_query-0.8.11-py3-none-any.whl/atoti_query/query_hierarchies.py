from atoti_core import BaseHierarchies, HierarchyKey, frozendict
from typing_extensions import override

from .query_hierarchy import QueryHierarchy


class QueryHierarchies(
    frozendict[HierarchyKey, QueryHierarchy], BaseHierarchies[QueryHierarchy]
):
    @override
    def __getitem__(self, key: HierarchyKey, /) -> QueryHierarchy:
        if isinstance(key, tuple):
            return super().__getitem__(key)
        matching_hierarchies = [
            hierarchy for hierarchy in self.values() if hierarchy.name == key
        ]
        if not matching_hierarchies:
            raise KeyError(key)
        if len(matching_hierarchies) == 1:
            return matching_hierarchies[0]
        raise self._multiple_hierarchies_error(key, matching_hierarchies)
