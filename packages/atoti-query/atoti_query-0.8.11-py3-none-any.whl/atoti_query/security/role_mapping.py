from __future__ import annotations

from collections.abc import Collection, Iterable, Mapping
from typing import (
    TYPE_CHECKING,
    Optional,
    Union,
    overload,
)
from warnings import warn

from atoti_core import (
    DEPRECATED_WARNING_CATEGORY,
    DelegateMutableMapping,
    ReactiveMutableSet,
)
from typing_extensions import override

from ._authentication_type import AuthenticationType
from ._service import Service

if TYPE_CHECKING:
    from _typeshed import SupportsKeysAndGetItem  # pylint: disable=nested-import


class _MappedRoles(ReactiveMutableSet[str]):
    def __init__(
        self, data: Collection[str], /, *, role_name: str, role_mapping: RoleMapping
    ) -> None:
        super().__init__(data)

        self._role_name = role_name
        self._role_mapping = role_mapping

    @override
    def _on_change(self, *, in_place: bool) -> None:
        if in_place:
            warn(
                "Mutating roles is deprecated. Reassign them instead.",
                category=DEPRECATED_WARNING_CATEGORY,
                stacklevel=2,
            )

        self._role_mapping[self._role_name] = self


_RoleMappingDescription = Union[Collection[str], _MappedRoles]


class RoleMapping(DelegateMutableMapping[str, _MappedRoles]):
    """Mapping from role or username coming from the authentication provider to roles to use in the session."""

    def __init__(
        self, *, authentication_type: AuthenticationType, service: Service
    ) -> None:
        super().__init__()

        self._authentication_type: AuthenticationType = authentication_type
        self._service = service

    @override
    def _get_underlying(self) -> dict[str, _MappedRoles]:
        role_mapping: Mapping[str, Collection[str]] = self._service.get_role_mapping(
            authentication_type=self._authentication_type
        )
        return {
            role_name: _MappedRoles(  # Replace with `role_name: frozenset(authorities)` in the next breaking release.
                authorities,
                role_name=role_name,
                role_mapping=self,
            )
            for role_name, authorities in role_mapping.items()
        }

    # Custom override with same value type as the one used in `update()`.
    @override
    def __setitem__(self, key: str, value: _RoleMappingDescription, /) -> None:
        self.update({key: value})

    @override
    def _update(self, other: Mapping[str, _RoleMappingDescription], /) -> None:
        for role_name, authorities in other.items():
            self._service.upsert_role_mapping(
                role_name,
                authentication_type=self._authentication_type,
                authorities=authorities,
            )

    @overload
    def update(
        self,
        __m: SupportsKeysAndGetItem[str, _RoleMappingDescription],
        **kwargs: _RoleMappingDescription,
    ) -> None: ...

    @overload
    def update(
        self,
        __m: Iterable[tuple[str, _RoleMappingDescription]],  # pylint: disable=no-iterable
        **kwargs: _RoleMappingDescription,
    ) -> None: ...

    @overload
    def update(self, **kwargs: _RoleMappingDescription) -> None: ...

    @override  # type:ignore[misc]
    # Custom override types on purpose so that `Iterable[str]` can be inserted.
    def update(  # pyright: ignore[reportInconsistentOverload]
        self,
        __m: Optional[
            Union[
                Mapping[str, _RoleMappingDescription],
                Iterable[tuple[str, _RoleMappingDescription]],  # pylint: disable=no-iterable
            ]
        ] = None,
        **kwargs: _RoleMappingDescription,
    ) -> None:
        other: dict[str, _RoleMappingDescription] = {}
        if __m is not None:
            other.update(__m)
        other.update(**kwargs)
        self._update(other)

    @override
    def _delete_keys(self, keys: Collection[str], /) -> None:
        for key in keys:
            self._service.remove_role_from_role_mapping(
                key, authentication_type=self._authentication_type
            )
