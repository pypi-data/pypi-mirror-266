from __future__ import annotations

from collections.abc import Collection, Mapping, MutableMapping
from typing import Optional

from atoti_core import DEPRECATED_WARNING_CATEGORY, DelegateMutableMapping
from typing_extensions import deprecated, override

from ._service import Service


class _BasicUser:
    def __init__(
        self,
        username: str,
        *,
        password: Optional[str] = None,
        basic_security: BasicSecurity,
    ):
        self._password = password
        self._username = username

        self._basic_security = basic_security

    @property
    def password(self) -> Optional[str]:
        return self._password

    @password.setter
    def password(self, password: str, /) -> None:
        self._basic_security.credentials[self.username] = password
        self._password = password

    @property
    def username(self) -> str:
        return self._username


class _BasicUsers(DelegateMutableMapping[str, _BasicUser]):
    def __init__(self, *, basic_security: BasicSecurity) -> None:
        super().__init__()

        self._basic_security = basic_security

    @override
    def _get_underlying(self) -> dict[str, _BasicUser]:
        return {
            username: _BasicUser(username, basic_security=self._basic_security)
            for username in self._basic_security.credentials
        }

    @override
    def _update(self, other: Mapping[str, _BasicUser]) -> None:
        self._basic_security.credentials.update(
            {user.username: str(user.password) for user in other.values()}
        )

    @override
    def _delete_keys(self, keys: Collection[str], /) -> None:
        for username in keys:
            del self._basic_security.credentials[username]


class BasicSecurity:
    """Manage basic security on the session.

    Note:
        This requires a config to be passed to :func:`atoti.Session.__init__`'s *authentication* parameter.
    """

    def __init__(
        self,
        *,
        credentials: Optional[MutableMapping[str, str]] = None,
        service: Service,
    ) -> None:
        self._credentials = credentials
        self._service = service

    @property
    def credentials(self) -> MutableMapping[str, str]:
        """Mapping from username to password.

        Note:
            At the moment, unlike the rest of the :class:`~atoti_query.security.Security` configuration, these credentials are transient (kept in memory).
            They are not stored in the :class:`user content storage <atoti.UserContentStorageConfig>` and thus will reset when the session stops.

        Use :attr:`~atoti_query.security.Security.individual_roles` to grant roles to the user.

        Example:
            >>> session = tt.Session(authentication=tt.BasicAuthenticationConfig())
            >>> session.security.basic.credentials
            {}
            >>> session.security.basic.credentials["elon"] = "X Æ A-12"
            >>> # The password can be changed:
            >>> session.security.basic.credentials["elon"] = "AE A-XII"
            >>> # But, for security reasons, it cannot be retrieved (accessing it will return a redacted string):
            >>> session.security.basic.credentials
            {'elon': '**REDACTED**'}
            >>> # Prevent user to authenticate through basic authentication:
            >>> del session.security.basic.credentials["elon"]
            >>> session.security.basic.credentials
            {}
        """
        if self._credentials is None:
            raise RuntimeError("Credentials can only be managed on local sessions.")

        return self._credentials

    @property
    @deprecated(
        "Managing users is deprecated. Use `Security.individual_roles` and `Security.basic.credentials` instead.",
        category=DEPRECATED_WARNING_CATEGORY,
    )
    def users(self) -> _BasicUsers:
        """Basic users.

        :meta private:
        """
        return _BasicUsers(basic_security=self)

    def create_user(
        self,
        username: str,
        *,
        password: Optional[str] = None,
    ) -> _BasicUser:
        """Add a user able to authenticate against the session using Basic Authentication.

        :meta private:
        """
        user = _BasicUser(username, password=password, basic_security=self)
        self._service.upsert_individual_roles(username, roles=[])
        self.users[username] = user  # pyright: ignore[reportDeprecated]
        return user
