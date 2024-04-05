# Adapted from https://github.com/activeviam/atoti-ui/blob/eb113a9164ee18443d35ce3bb9e09111c76c4db2/packages/mdx/src/mdx.types.ts.

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import field
from typing import Annotated, Generic, Literal, Optional, TypeVar, Union

from atoti_core import (
    PYDANTIC_CONFIG as __PYDANTIC_CONFIG,
    FrozenSequence,
    HierarchyIdentifier,
    LevelIdentifier,
    MeasureIdentifier,
    create_camel_case_alias_generator,
    keyword_only_dataclass,
)
from pydantic import AliasChoices, ConfigDict, Discriminator, Field
from pydantic.dataclasses import dataclass
from typing_extensions import Self

_MEASURES_DIMENSION = "Measures"


_PYDANTIC_CONFIG: ConfigDict = {
    **__PYDANTIC_CONFIG,
    "alias_generator": create_camel_case_alias_generator(
        force_aliased_attribute_names={"element_type"}
    ),
    "arbitrary_types_allowed": False,
    "extra": "ignore",
}


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class MdxLiteral:
    element_type: Literal["Literal"] = field(default="Literal", init=False, repr=False)
    type: Literal["KEYWORD", "SCALAR", "STRING"]
    value: str

    @classmethod
    def keyword(cls, value: str, /) -> Self:
        return cls(type="KEYWORD", value=value)

    @classmethod
    def scalar(cls, value: str, /) -> Self:
        return cls(type="SCALAR", value=value)

    @classmethod
    def string(cls, value: str, /) -> Self:
        return cls(type="STRING", value=value)


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class MdxIdentifier:
    element_type: Literal["Identifier"] = field(
        default="Identifier", init=False, repr=False
    )
    quoting: str = field(default="QUOTED", init=False, repr=False)
    value: str

    @classmethod
    def of(cls, value: str, /) -> Self:
        return cls(value=value)


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class _AMdxCompoundIdentifier:
    element_type: Literal["CompoundIdentifier"] = field(
        default="CompoundIdentifier", init=False, repr=False
    )
    identifiers: FrozenSequence[MdxIdentifier]


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class MdxHierarchyCompoundIdentifier(_AMdxCompoundIdentifier):
    type: Literal["hierarchy"] = field(default="hierarchy", init=False, repr=False)
    dimension_name: str
    hierarchy_name: str

    @classmethod
    def of(cls, hierarchy_identifier: HierarchyIdentifier, /) -> Self:
        return cls(
            identifiers=[
                MdxIdentifier.of(hierarchy_identifier.dimension_name),
                MdxIdentifier.of(hierarchy_identifier.hierarchy_name),
            ],
            dimension_name=hierarchy_identifier.dimension_name,
            hierarchy_name=hierarchy_identifier.hierarchy_name,
        )


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class MdxLevelCompoundIdentifier(_AMdxCompoundIdentifier):
    type: Literal["level"] = field(default="level", init=False, repr=False)
    dimension_name: str
    hierarchy_name: str
    level_name: str

    @classmethod
    def of(cls, level_identifier: LevelIdentifier, /) -> Self:
        return cls(
            identifiers=[
                MdxIdentifier.of(level_identifier.hierarchy_identifier.dimension_name),
                MdxIdentifier.of(level_identifier.hierarchy_identifier.hierarchy_name),
                MdxIdentifier.of(level_identifier.level_name),
            ],
            dimension_name=level_identifier.hierarchy_identifier.dimension_name,
            hierarchy_name=level_identifier.hierarchy_identifier.hierarchy_name,
            level_name=level_identifier.level_name,
        )


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class MdxMeasureCompoundIdentifier(_AMdxCompoundIdentifier):
    type: Literal["measure"] = field(default="measure", init=False, repr=False)
    measure_name: str

    @classmethod
    def of(cls, measure_identifier: MeasureIdentifier, /) -> Self:
        return cls(
            identifiers=[
                MdxIdentifier.of(_MEASURES_DIMENSION),
                MdxIdentifier.of(measure_identifier.measure_name),
            ],
            measure_name=measure_identifier.measure_name,
        )


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class MdxMemberCompoundIdentifier(_AMdxCompoundIdentifier):
    type: Literal["member"] = field(default="member", init=False, repr=False)
    dimension_name: str
    hierarchy_name: str
    level_name: str
    path: FrozenSequence[str]

    @classmethod
    def of(
        cls,
        *path: str,
        level_identifier: LevelIdentifier,
        hierarchy_first_level_name: str,
    ) -> Self:
        return cls(
            identifiers=[
                MdxIdentifier.of(level_identifier.hierarchy_identifier.dimension_name),
                MdxIdentifier.of(level_identifier.hierarchy_identifier.hierarchy_name),
                MdxIdentifier.of(hierarchy_first_level_name),
                *[MdxIdentifier.of(value) for value in path],
            ],
            dimension_name=level_identifier.hierarchy_identifier.dimension_name,
            hierarchy_name=level_identifier.hierarchy_identifier.hierarchy_name,
            level_name=level_identifier.level_name,
            path=path,
        )


MdxCompoundIdentifier = Annotated[
    Union[
        MdxMeasureCompoundIdentifier,
        MdxMemberCompoundIdentifier,
        MdxLevelCompoundIdentifier,
        MdxHierarchyCompoundIdentifier,
    ],
    Discriminator("type"),
]


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class MdxFunction:
    element_type: Literal["Function"] = field(
        default="Function", init=False, repr=False
    )
    arguments: FrozenSequence[MdxExpression]
    name: str
    syntax: Literal["Braces", "Function", "Infix", "Parentheses", "Property"]

    def __post_init__(self) -> None:
        if self.syntax == "Property":
            assert len(self.arguments) == 1

    @classmethod
    def braces(cls, arguments: Sequence[MdxExpression], /) -> Self:
        return cls(arguments=arguments, name=r"{}", syntax="Braces")

    @classmethod
    def function(cls, name: str, arguments: Sequence[MdxExpression], /) -> Self:
        return cls(arguments=arguments, name=name, syntax="Function")

    @classmethod
    def infix(cls, name: str, arguments: Sequence[MdxExpression], /) -> Self:
        return cls(arguments=arguments, name=name, syntax="Infix")

    @classmethod
    def parentheses(cls, arguments: Sequence[MdxExpression], /) -> Self:
        return cls(arguments=arguments, name="()", syntax="Parentheses")

    @classmethod
    def property(cls, name: str, argument: MdxExpression, /) -> Self:
        return cls(arguments=[argument], name=name, syntax="Property")


MdxExpression = Annotated[
    Union[MdxLiteral, MdxIdentifier, MdxCompoundIdentifier, MdxFunction],
    Discriminator("element_type"),
]

ColumnsAxisName = Literal["COLUMNS"]
RowsAxisName = Literal["ROWS"]
RegularAxisName = Literal[ColumnsAxisName, RowsAxisName]
SlicerAxisName = Literal["SLICER"]
AxisName = Literal[RegularAxisName, SlicerAxisName]
AxisNameT_co = TypeVar("AxisNameT_co", bound=AxisName, covariant=True)


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class MdxAxis(Generic[AxisNameT_co]):
    element_type: Literal["Axis"] = field(default="Axis", init=False, repr=False)
    expression: MdxExpression
    name: AxisNameT_co
    properties: FrozenSequence[MdxAst] = field(default=(), init=False, repr=False)
    non_empty: bool = False

    def __post_init__(self) -> None:
        if self.name == "SLICER":
            assert not self.non_empty


MdxAxisBound = MdxAxis[AxisName]


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class MdxFromClause:
    element_type: Literal["From"] = field(default="From", init=False, repr=False)
    cube_name: str


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class _AMdxSelect:
    axes: FrozenSequence[MdxAxis[RegularAxisName]]
    from_clause: Annotated[
        Union[MdxSubSelect, MdxFromClause],
        Field(
            validation_alias=AliasChoices("from_clause", "from"),
            serialization_alias="from",
        ),
    ]
    slicer_axis: Optional[MdxAxis[SlicerAxisName]] = None


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class MdxSelect(_AMdxSelect):
    element_type: Literal["Select"] = field(default="Select", init=False, repr=False)
    with_clause: FrozenSequence[object] = field(default=(), init=False, repr=False)


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class MdxSubSelect(_AMdxSelect):
    element_type: Literal["SubSelect"] = field(
        default="SubSelect", init=False, repr=False
    )
    non_visual: bool = field(default=False, init=False, repr=False)


MdxAst = Annotated[
    Union[MdxExpression, MdxAxisBound, MdxFromClause, MdxSelect, MdxSubSelect],
    Discriminator("element_type"),
]
