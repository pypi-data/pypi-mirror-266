from collections.abc import Mapping
from functools import cache, cached_property
from typing import TypedDict, cast
from urllib.parse import urljoin

from atoti_core import (
    PYDANTIC_CONFIG as _PYDANTIC_CONFIG,
    fetch_json,
    keyword_only_dataclass,
)
from pydantic.dataclasses import dataclass
from typing_extensions import override

from .auth import Auth
from .token_authentication import TokenAuthentication


class _OpenIdConfiguration(TypedDict):
    token_endpoint: str


@cache
def _fetch_token_endpoint_url(*, issuer_url: str) -> str:
    configuration_url = urljoin(issuer_url, ".well-known/openid-configuration")
    configuration = cast(_OpenIdConfiguration, fetch_json(configuration_url).body)
    return configuration["token_endpoint"]


class _ResponseBody(TypedDict):
    access_token: str
    token_type: str


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class OAuth2ResourceOwnerPasswordAuthentication(Auth):
    """This :class:`atoti_query.Auth` relies on OAuth 2's `Resource Owner Password Credentials Grant <https://datatracker.ietf.org/doc/html/rfc6749#section-4.3>`__.

    See Also:
        :attr:`atoti.OidcConfig.access_token_format`.
    """

    username: str
    password: str
    issuer_url: str
    client_id: str
    client_secret: str

    @override
    def __call__(self, url: str) -> Mapping[str, str]:
        return self._token_authentication(url)

    @cached_property
    def _token_authentication(self) -> TokenAuthentication:
        body = cast(
            _ResponseBody,
            fetch_json(
                _fetch_token_endpoint_url(issuer_url=self.issuer_url),
                body={
                    "grant_type": "password",
                    "username": self.username,
                    "password": self.password,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            ).body,
        )
        return TokenAuthentication(
            token=body["access_token"], token_type=body["token_type"]
        )
