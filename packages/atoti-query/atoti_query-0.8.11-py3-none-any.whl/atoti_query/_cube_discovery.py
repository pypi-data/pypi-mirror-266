from __future__ import annotations

from functools import cached_property
from typing import Optional

from atoti_core import (
    PYDANTIC_CONFIG as __PYDANTIC_CONFIG,
    FrozenSequence,
    create_camel_case_alias_generator,
    frozendict,
    keyword_only_dataclass,
)
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

_PYDANTIC_CONFIG: ConfigDict = {
    **__PYDANTIC_CONFIG,
    "alias_generator": create_camel_case_alias_generator(),
    "arbitrary_types_allowed": False,
    "extra": "ignore",
}


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class DiscoveryLevel:
    name: str
    caption: str
    type: str


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class DiscoveryHierarchy:
    name: str
    caption: str
    slicing: bool
    levels: FrozenSequence[DiscoveryLevel]

    @cached_property
    def name_to_level(self) -> frozendict[str, DiscoveryLevel]:
        return frozendict({level.name: level for level in self.levels})


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class DiscoveryDimension:
    name: str
    caption: str
    type: str
    hierarchies: FrozenSequence[DiscoveryHierarchy]

    @cached_property
    def name_to_hierarchy(self) -> frozendict[str, DiscoveryHierarchy]:
        return frozendict({hierarchy.name: hierarchy for hierarchy in self.hierarchies})


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class DiscoveryMeasure:
    name: str
    caption: str
    visible: bool
    description: Optional[str] = None
    folder: Optional[str] = None
    format_string: Optional[str] = None


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class DefaultMember:
    caption_path: FrozenSequence[str]
    dimension: str
    hierarchy: str
    path: FrozenSequence[str]


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class DiscoveryCube:
    name: str
    default_members: FrozenSequence[DefaultMember]
    dimensions: FrozenSequence[DiscoveryDimension]
    measures: FrozenSequence[DiscoveryMeasure]

    @cached_property
    def name_to_dimension(self) -> frozendict[str, DiscoveryDimension]:
        return frozendict({dimension.name: dimension for dimension in self.dimensions})

    @cached_property
    def name_to_measure(self) -> frozendict[str, DiscoveryMeasure]:
        return frozendict({measure.name: measure for measure in self.measures})


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class DiscoveryCatalog:
    name: str
    cubes: FrozenSequence[DiscoveryCube]

    @cached_property
    def name_to_cube(self) -> frozendict[str, DiscoveryCube]:
        return frozendict({cube.name: cube for cube in self.cubes})


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class CubeDiscovery:
    catalogs: FrozenSequence[DiscoveryCatalog]

    @cached_property
    def name_to_catalog(self) -> frozendict[str, DiscoveryCatalog]:
        return frozendict({catalog.name: catalog for catalog in self.catalogs})

    def get_cube(self, cube_name: str, /) -> DiscoveryCube:
        try:
            return next(
                (
                    cube
                    for catalog in self.catalogs
                    for cube in catalog.cubes
                    if cube.name == cube_name
                ),
            )
        except StopIteration as error:
            raise ValueError(f"No cube named `{cube_name}` in the catalogs.") from error
