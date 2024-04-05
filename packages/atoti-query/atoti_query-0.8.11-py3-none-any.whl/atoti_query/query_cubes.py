from atoti_core import BaseCubes, frozendict

from .query_cube import QueryCube


class QueryCubes(frozendict[str, QueryCube], BaseCubes[QueryCube]): ...
