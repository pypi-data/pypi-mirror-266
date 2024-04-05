from __future__ import annotations

from typing import Optional

from atoti_core import (
    HierarchyIdentifier,
    LevelIdentifier,
    MeasureIdentifier,
    frozendict,
)

from ._cube_discovery import CubeDiscovery, DiscoveryCube, DiscoveryHierarchy
from ._execute_gaq import ExecuteGaq
from ._query_mdx import QueryMdx
from .query_cube import QueryCube
from .query_cubes import QueryCubes
from .query_hierarchies import QueryHierarchies
from .query_hierarchy import QueryHierarchy
from .query_level import QueryLevel
from .query_measure import QueryMeasure
from .query_measures import QueryMeasures


def _create_hierarchy(
    hierarchy: DiscoveryHierarchy,
    /,
    *,
    dimension_name: str,
) -> QueryHierarchy:
    hierarchy_identifier = HierarchyIdentifier(dimension_name, hierarchy.name)
    levels = frozendict(
        {
            level.name: QueryLevel(LevelIdentifier(hierarchy_identifier, level.name))
            for level in hierarchy.levels
            if level.type != "ALL"
        }
    )
    return QueryHierarchy(
        hierarchy_identifier,
        levels=levels,
        slicing=hierarchy.slicing,
    )


def _create_cube(
    cube: DiscoveryCube,
    /,
    *,
    execute_gaq: Optional[ExecuteGaq] = None,
    query_mdx: QueryMdx,
) -> QueryCube:
    hierarchies = QueryHierarchies(
        {
            (dimension.name, hierarchy.name): _create_hierarchy(
                hierarchy, dimension_name=dimension.name
            )
            for dimension in cube.dimensions
            if dimension.name != "Epoch"
            for hierarchy in dimension.hierarchies
        }
    )
    measures = QueryMeasures(
        {
            measure.name: QueryMeasure(
                MeasureIdentifier(measure.name),
                description=measure.description,
                folder=measure.folder,
                formatter=measure.format_string,
                visible=measure.visible,
            )
            for measure in cube.measures
        }
    )
    return QueryCube(
        cube.name,
        cube=cube,
        execute_gaq=execute_gaq,
        hierarchies=hierarchies,
        measures=measures,
        query_mdx=query_mdx,
    )


def create_query_cubes_from_discovery(
    discovery: CubeDiscovery,
    /,
    *,
    execute_gaq: Optional[ExecuteGaq] = None,
    query_mdx: QueryMdx,
) -> QueryCubes:
    return QueryCubes(
        {
            cube.name: _create_cube(cube, execute_gaq=execute_gaq, query_mdx=query_mdx)
            for catalog in discovery.catalogs
            for cube in catalog.cubes
        }
    )
