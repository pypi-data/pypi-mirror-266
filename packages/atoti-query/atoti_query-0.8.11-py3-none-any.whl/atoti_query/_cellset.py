from __future__ import annotations

from collections.abc import Collection
from dataclasses import asdict
from functools import cached_property
from typing import Annotated, Optional, Union

from atoti_core import (
    PYDANTIC_CONFIG as __PYDANTIC_CONFIG,
    FrozenSequence,
    create_camel_case_alias_generator,
    frozendict,
    keyword_only_dataclass,
)
from pydantic import ConfigDict, PlainSerializer
from pydantic.dataclasses import dataclass

from ._cube_discovery import DefaultMember

_PYDANTIC_CONFIG: ConfigDict = {
    **__PYDANTIC_CONFIG,
    "arbitrary_types_allowed": False,
    "extra": "ignore",
}


_PYDANTIC_CONFIG_WITH_ALIAS: ConfigDict = {
    **_PYDANTIC_CONFIG,
    "alias_generator": create_camel_case_alias_generator(),
}


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG_WITH_ALIAS, frozen=True)
class CellSetHierarchy:
    dimension: str
    hierarchy: str


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG_WITH_ALIAS, frozen=True)
class CellSetMember:
    caption_path: FrozenSequence[str]
    name_path: FrozenSequence[str]


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG_WITH_ALIAS, frozen=True)
class CellSetAxis:
    hierarchies: FrozenSequence[CellSetHierarchy]
    id: int
    positions: FrozenSequence[FrozenSequence[CellSetMember]]

    @cached_property
    def max_level_per_hierarchy(self) -> tuple[int, ...]:
        """This property always existed in cell sets returned by the WebSocket API but was only added to those returned by the HTTP API in Atoti Server 6.0.9.

        Using it helps keeping the logic to convert a cell set to a table similar to the one used by Atoti UI.
        """
        return tuple(
            max(
                (
                    len(position[hierarchy_index].name_path)
                    for position in self.positions
                ),
                default=0,
            )
            for hierarchy_index in range(len(self.hierarchies))
        )


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class CellSetCellProperties:
    BACK_COLOR: Optional[Union[int, str]] = None
    FONT_FLAGS: Optional[int] = None
    FONT_NAME: Optional[str] = None
    FONT_SIZE: Optional[int] = None
    FORE_COLOR: Optional[Union[int, str]] = None

    @cached_property
    def is_empty(self, /) -> bool:
        return all(value is None for value in asdict(self).values())


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG_WITH_ALIAS, frozen=True)
class CellSetCell:
    ordinal: int
    properties: CellSetCellProperties
    value: object = None
    formatted_value: Optional[str] = None

    @cached_property
    def pythonic_formatted_value(self) -> str:
        return (
            str(self.value)
            if isinstance(self.value, bool) or self.formatted_value is None
            else self.formatted_value
        )


def _sort_cells(cells: Collection[CellSetCell], /) -> list[CellSetCell]:
    return sorted(cells, key=lambda cell: cell.ordinal)


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG_WITH_ALIAS, frozen=True)
class CellSet:
    axes: FrozenSequence[CellSetAxis]
    cells: Annotated[
        FrozenSequence[CellSetCell],
        # To keep snapshots stable.
        PlainSerializer(_sort_cells, when_used="json"),
    ]
    cube: str
    default_members: FrozenSequence[DefaultMember]

    @cached_property
    def ordinal_to_cell(self) -> frozendict[int, CellSetCell]:
        return frozendict({cell.ordinal: cell for cell in self.cells})
