from ._service import Service
from .default_roles import DefaultRoles


class KerberosSecurity:
    """Manage Kerberos security on the session.

    Note:
        This requires a :class:`~atoti.KerberosConfig` to be passed to :func:`atoti.Session.__init__`'s *authentication* parameter.

    See Also:
        :attr:`~atoti_query.security.Security.ldap` for a similar usage example.
    """

    def __init__(
        self,
        *,
        default_roles: DefaultRoles,
        service: Service,
    ) -> None:
        self._default_roles = default_roles
        self._service = service

    @property
    def default_roles(self) -> DefaultRoles:
        return self._default_roles
