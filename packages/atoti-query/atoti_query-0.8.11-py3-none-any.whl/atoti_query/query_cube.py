from __future__ import annotations

from dataclasses import replace
from typing import Any, Literal, Optional

import pandas as pd
from atoti_core import (
    BASE_SCENARIO_NAME as _BASE_SCENARIO_NAME,
    DEFAULT_QUERY_TIMEOUT as _DEFAULT_QUERY_TIMEOUT,
    QUERY_DOC as _QUERY_DOC,
    BaseCube,
    BaseLevel,
    BaseMeasure,
    Context,
    Duration,
    QueryFilter,
    SequenceOrDeprecatedSet,
    doc,
    frozendict,
    get_query_args_doc,
)
from typing_extensions import override

from ._cube_discovery import DiscoveryCube
from ._execute_gaq import ExecuteGaq
from ._generate_mdx import generate_mdx
from ._is_gaq_filter import is_gaq_filter
from ._query_mdx import QueryMdx
from ._query_private_parameters import QueryPrivateParameters
from ._stringify_mdx import stringify_mdx
from .query_hierarchies import QueryHierarchies
from .query_levels import QueryLevels
from .query_measures import QueryMeasures
from .query_result import QueryResult


class QueryCube(BaseCube[QueryHierarchies, QueryLevels, QueryMeasures]):
    def __init__(
        self,
        name: str,
        /,
        *,
        cube: DiscoveryCube,
        execute_gaq: Optional[ExecuteGaq],
        hierarchies: QueryHierarchies,
        measures: QueryMeasures,
        query_mdx: QueryMdx,
    ) -> None:
        super().__init__(name, hierarchies=hierarchies, measures=measures)

        self._cube = cube
        self._execute_gaq = execute_gaq
        self._query_mdx = query_mdx

    @property
    @override
    def levels(self) -> QueryLevels:
        """Levels of the cube."""
        return QueryLevels(hierarchies=self.hierarchies)

    @doc(_QUERY_DOC, args=get_query_args_doc(is_query_session=True))
    @override
    def query(
        self,
        *measures: BaseMeasure,
        context: Context = frozendict(),
        filter: Optional[QueryFilter] = None,  # noqa: A002
        include_empty_rows: bool = False,
        include_totals: bool = False,
        levels: SequenceOrDeprecatedSet[BaseLevel] = (),
        mode: Literal["pretty", "raw"] = "pretty",
        scenario: str = _BASE_SCENARIO_NAME,
        timeout: Duration = _DEFAULT_QUERY_TIMEOUT,
        **kwargs: Any,
    ) -> pd.DataFrame:
        private_parameters = QueryPrivateParameters(**kwargs)

        level_identifiers = [level._identifier for level in levels]
        measure_identifiers = [measure._identifier for measure in measures]

        if (
            mode == "raw"
            and self._execute_gaq
            and not context
            and (filter is None or is_gaq_filter(filter))
        ):
            return self._execute_gaq(
                cube_name=self.name,
                filter=filter,
                include_empty_rows=include_empty_rows,
                include_totals=include_totals,
                level_identifiers=level_identifiers,
                measure_identifiers=measure_identifiers,
                scenario=scenario,
                timeout=timeout,
            )

        mdx_ast = generate_mdx(
            cube=self._cube,
            filter=filter,
            include_empty_rows=include_empty_rows,
            include_totals=include_totals,
            level_identifiers=level_identifiers,
            measure_identifiers=measure_identifiers,
            scenario=scenario,
        )
        mdx = stringify_mdx(mdx_ast)

        query_result = self._query_mdx(
            mdx,
            context=context,
            get_data_types=private_parameters.get_data_types,
            keep_totals=include_totals,
            mode=mode,
            timeout=timeout,
        )

        # Always use an MDX including totals because Atoti UI 5 relies only on context values to show/hide totals.
        if (
            not include_totals
            and isinstance(query_result, QueryResult)
            and query_result._atoti_metadata
            and query_result._atoti_metadata.widget_conversion_details
        ):
            mdx_ast = generate_mdx(
                cube=self._cube,
                filter=filter,
                include_empty_rows=include_empty_rows,
                include_totals=True,
                level_identifiers=level_identifiers,
                measure_identifiers=measure_identifiers,
                scenario=scenario,
            )
            mdx = stringify_mdx(mdx_ast)
            query_result._atoti_metadata = replace(
                query_result._atoti_metadata,
                widget_conversion_details=replace(
                    query_result._atoti_metadata.widget_conversion_details, mdx=mdx
                ),
            )

        return query_result
