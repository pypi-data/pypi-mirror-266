from collections.abc import Mapping
from typing import Protocol


class Auth(Protocol):
    """Called with the URL of the request against a :class:`atoti_query.QuerySession` and returning the HTTP headers necessary to authenticate it.

    There are some built-in implementations:

    * :class:`atoti_query.BasicAuthentication`
    * :class:`atoti_query.OAuth2ResourceOwnerPasswordAuthentication`
    * :class:`atoti_query.TokenAuthentication`
    """

    def __call__(self, url: str, /) -> Mapping[str, str]: ...
