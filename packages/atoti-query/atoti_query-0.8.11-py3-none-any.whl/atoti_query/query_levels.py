from typing import Optional

from atoti_core import BaseLevels, raise_multiple_levels_with_same_name_error
from typing_extensions import override

from .query_hierarchies import QueryHierarchies
from .query_level import QueryLevel


class QueryLevels(BaseLevels[QueryHierarchies, QueryLevel]):
    """Flat representation of all the levels in the cube."""

    @override
    def _find_level(
        self,
        level_name: str,
        *,
        dimension_name: Optional[str] = None,
        hierarchy_name: Optional[str] = None,
    ) -> QueryLevel:
        if not dimension_name:
            if not hierarchy_name:
                level = self._flatten()[level_name]
                if level is not None:
                    return level
                hierarchies = [
                    hierarchy
                    for key, hierarchy in self._hierarchies.items()
                    if level_name == (key if isinstance(key, str) else key[1])
                ]
                raise_multiple_levels_with_same_name_error(
                    level_name,
                    hierarchies=hierarchies,
                )

            return self._hierarchies[hierarchy_name].levels[level_name]

        assert hierarchy_name is not None

        return self._hierarchies[dimension_name, hierarchy_name].levels[level_name]
