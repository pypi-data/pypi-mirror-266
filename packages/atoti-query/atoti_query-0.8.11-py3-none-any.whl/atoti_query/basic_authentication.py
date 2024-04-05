from base64 import b64encode
from collections.abc import Mapping

from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass
from typing_extensions import override

from .auth import Auth
from .token_authentication import TokenAuthentication


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class BasicAuthentication(Auth):
    """:class:`atoti_query.Auth` relying on `basic authentication <https://en.wikipedia.org/wiki/Basic_access_authentication>`__.

    See Also:
        :class:`atoti.BasicAuthenticationConfig`.
    """

    username: str
    password: str

    @override
    def __call__(self, url: str) -> Mapping[str, str]:
        return self._token_authentication(url)

    @property
    def _token_authentication(self) -> TokenAuthentication:
        plain_credentials = f"{self.username}:{self.password}"
        token = str(b64encode(plain_credentials.encode("ascii")), "utf8")
        return TokenAuthentication(
            token=token,
            token_type="Basic",  # noqa: S106
        )
