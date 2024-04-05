from __future__ import annotations

from collections import defaultdict
from collections.abc import (
    Collection,
    Iterator,
    Mapping,
    MutableMapping,
    Set as AbstractSet,
)
from typing import Union

from atoti_core import DelegateMutableMapping, ReactiveMutableSet
from typing_extensions import override

from ._column_key import ColumnKey
from ._restriction import Restriction
from ._restriction_from_mapping import restriction_from_mapping
from ._restriction_to_dict import restriction_to_dict
from ._service import Service


class _AllowedMembers(ReactiveMutableSet[str]):
    def __init__(
        self, data: Collection[str], /, *, column_key: ColumnKey, role: Role
    ) -> None:
        super().__init__(data)

        self._column_key = column_key
        self._role = role

    @override
    def _on_change(self, *, in_place: bool) -> None:
        self._role.restrictions[self._column_key] = self


class Restrictions(MutableMapping[ColumnKey, _AllowedMembers]):
    def __init__(
        self,
        restrictions: MutableMapping[ColumnKey, _AllowedMembers],
        /,
        *,
        role: Role,
        service: Service,
    ) -> None:
        self._restrictions = restrictions
        self._role = role
        self._service = service

    @override
    def __setitem__(
        self, key: ColumnKey, value: Union[Collection[str], _AllowedMembers], /
    ) -> None:
        if isinstance(value, _AllowedMembers):
            self._restrictions[key] = value
        else:
            self._restrictions[key] = _AllowedMembers(
                value,
                column_key=key,
                role=self._role,
            )

        self._service.upsert_restriction(self._restriction, role_name=self._role.name)

    @override
    def __getitem__(self, key: ColumnKey, /) -> _AllowedMembers:
        return self._restrictions[key]

    @override
    def __delitem__(self, key: ColumnKey, /) -> None:
        del self._restrictions[key]
        self._service.upsert_restriction(self._restriction, role_name=self._role.name)

    @override
    def __iter__(self) -> Iterator[ColumnKey]:
        return iter(self._restrictions)

    @override
    def __len__(self) -> int:
        return len(self._restrictions)

    @property
    def _restriction(self) -> Restriction:
        restriction: dict[str, dict[str, list[str]]] = defaultdict(dict)

        for (table_name, column_name), members in self.items():
            restriction[table_name][column_name] = list(members)

        return restriction_from_mapping(restriction)


class Role:
    def __init__(
        self,
        name: str,
        /,
        *,
        restrictions: Mapping[ColumnKey, Collection[str]],
        _service: Service,
    ):
        self._service = _service
        self._name = name
        self._restrictions: Restrictions = self._restrictions_from_mapping(restrictions)

    @property
    def name(self) -> str:
        return self._name

    @property
    def restrictions(self) -> Restrictions:
        return self._restrictions

    @restrictions.setter
    def restrictions(
        self, value: Union[Mapping[ColumnKey, Collection[str]], Restrictions], /
    ) -> None:
        self._restrictions = (
            value
            if isinstance(value, Restrictions)
            else self._restrictions_from_mapping(value)
        )
        self._service.upsert_restriction(
            self._restrictions._restriction, role_name=self.name
        )

    @override
    def __repr__(self) -> str:
        return repr({"restrictions": self._restrictions})

    def _restrictions_from_mapping(
        self, restrictions: Mapping[ColumnKey, Collection[str]], /
    ) -> Restrictions:
        return Restrictions(
            {
                key: _AllowedMembers(
                    value,
                    column_key=key,
                    role=self,
                )
                for key, value in restrictions.items()
            },
            role=self,
            service=self._service,
        )


class Roles(DelegateMutableMapping[str, Role]):
    def __init__(self, *, service: Service) -> None:
        super().__init__()

        self._service = service

    @override
    def _get_underlying(self) -> dict[str, Role]:
        return {
            role_name: Role(
                role_name,
                restrictions={
                    (table_name, column_name): elements
                    for table_name, column_restriction in restriction_to_dict(
                        restriction
                    ).items()
                    for column_name, elements in column_restriction.items()
                },
                _service=self._service,
            )
            for role_name, restriction in self._service.restrictions.items()
        }

    @override
    def _update(self, other: Mapping[str, Role], /) -> None:
        for role_name, role in other.items():
            self._service.upsert_restriction(
                role.restrictions._restriction, role_name=role_name
            )

    @override
    def _delete_keys(self, keys: AbstractSet[str], /) -> None:
        for key in keys:
            self._service.delete_restriction(key)
