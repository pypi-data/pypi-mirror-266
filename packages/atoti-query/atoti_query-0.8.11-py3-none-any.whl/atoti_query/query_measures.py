from atoti_core import BaseMeasures, frozendict

from .query_measure import QueryMeasure


class QueryMeasures(frozendict[str, QueryMeasure], BaseMeasures[QueryMeasure]): ...
