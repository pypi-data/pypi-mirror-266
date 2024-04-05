from __future__ import annotations

import json
from collections.abc import Collection
from dataclasses import field
from http import HTTPStatus
from typing import Literal, Optional, Union
from urllib.error import HTTPError
from urllib.parse import urlencode

from atoti_core import (
    PYDANTIC_CONFIG as __PYDANTIC_CONFIG,
    ActiveViamClient,
    FrozenMapping,
    FrozenSequence,
    create_camel_case_alias_generator,
    keyword_only_dataclass,
)
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

_PYDANTIC_CONFIG: ConfigDict = {
    **__PYDANTIC_CONFIG,
    "alias_generator": create_camel_case_alias_generator(
        force_aliased_attribute_names={"is_directory"}
    ),
    "arbitrary_types_allowed": False,
    "extra": "ignore",
}


_USER_CONTENT_STORAGE_NAMESPACE = "activeviam/content"


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class _ContentEntry:
    timestamp: int
    last_editor: str
    owners: FrozenSequence[str]
    readers: FrozenSequence[str]
    can_read: bool
    can_write: bool


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class DirectoryContentEntry(_ContentEntry):
    is_directory: Literal[True] = field(default=True, repr=False)


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class DirectoryContentTree:
    entry: DirectoryContentEntry
    children: FrozenMapping[str, ContentTree] = field(default_factory=dict)


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class FileContentEntry(_ContentEntry):
    content: str
    is_directory: Literal[False] = field(default=False, repr=False)


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class FileContentTree:
    entry: FileContentEntry


ContentTree = Union[DirectoryContentTree, FileContentTree]


class ContentClient:
    def __init__(self, *, client: ActiveViamClient) -> None:
        self._client = client

    def get(self, path: str, /) -> Optional[ContentTree]:
        try:
            response = self._client.fetch_json(  # type: ignore[var-annotated]
                namespace=_USER_CONTENT_STORAGE_NAMESPACE,
                query=urlencode({"path": path}),
                response_body_type=ContentTree,  # type: ignore[arg-type]
                route="files",
            )
        except HTTPError as error:
            if error.code == HTTPStatus.NOT_FOUND:
                return None
            raise
        else:
            return response.body  # type: ignore[no-any-return]

    def create(
        self,
        path: str,
        /,
        *,
        content: object,
        owners: Collection[str],
        readers: Collection[str],
    ) -> None:
        self._client.fetch_json(
            body={
                "content": json.dumps(content),
                "owners": owners,
                "readers": readers,
                "overwrite": True,
                "recursive": True,
            },
            check_response_content_type=False,
            method="PUT",
            namespace=_USER_CONTENT_STORAGE_NAMESPACE,
            query=urlencode({"path": path}),
            route="files",
        )

    def delete(self, path: str, /) -> None:
        self._client.fetch_json(
            check_response_content_type=False,
            method="DELETE",
            namespace=_USER_CONTENT_STORAGE_NAMESPACE,
            query=urlencode({"path": path}),
            route="files",
        )
