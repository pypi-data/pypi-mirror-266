from collections.abc import Mapping

from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass
from typing_extensions import override

from .auth import Auth


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class TokenAuthentication(Auth):
    """Also called "Bearer authentication", this :class:`atoti_query.Auth`, passes the given token to the HTTP :guilabel:`Authorization` header of the request being made."""

    token: str
    token_type: str = "Bearer"

    @override
    def __call__(
        self,
        url: str,
    ) -> Mapping[str, str]:
        return self._headers

    @property
    def _headers(self) -> Mapping[str, str]:
        return {"Authorization": f"{self.token_type} {self.token}"}
