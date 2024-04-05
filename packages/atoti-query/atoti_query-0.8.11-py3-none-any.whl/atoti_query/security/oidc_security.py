from ._service import Service
from .default_roles import DefaultRoles
from .role_mapping import RoleMapping


class OidcSecurity:
    """Manage OIDC security on the session.

    Note:
        This requires an :class:`~atoti.OidcConfig` to be passed to :func:`atoti.Session.__init__`'s *authentication* parameter.

    Example:
        >>> import os
        >>> session = tt.Session(
        ...     authentication=tt.OidcConfig(
        ...         provider_id="auth0",
        ...         issuer_url=os.environ["AUTH0_ISSUER"],
        ...         client_id=os.environ["AUTH0_CLIENT_ID"],
        ...         client_secret=os.environ["AUTH0_CLIENT_SECRET"],
        ...         name_claim="email",
        ...         scopes={"email", "profile", "username"},
        ...         roles_claims={"https://activeviam.com/roles"},
        ...     ),
        ...     port=1234,
        ... )
        >>> table = session.create_table(
        ...     "Restrictions example", types={"Country": tt.STRING}
        ... )
        >>> session.security.restrictions.update(
        ...     {
        ...         "ROLE_FRANCE": table["Country"] == "France",
        ...         "ROLE_UK": table["Country"] == "UK",
        ...     }
        ... )

        Roles from the authentication provider's ID Token can be mapped to roles in the session:

        >>> session.security.oidc.role_mapping.update(
        ...     {"atoti user": {"ROLE_USER"}, "France": {"ROLE_FRANCE"}}
        ... )
        >>> session.security.oidc.role_mapping
        {'atoti user': {'ROLE_USER'}, 'France': {'ROLE_FRANCE'}}

        Default roles can be given to users who have been granted no individual and mapped roles:

        >>> session.security.oidc.default_roles.add("ROLE_UK")
        >>> session.security.oidc.default_roles
        {'ROLE_UK'}

    """

    def __init__(
        self,
        *,
        default_roles: DefaultRoles,
        role_mapping: RoleMapping,
        service: Service,
    ) -> None:
        self._default_roles = default_roles
        self._role_mapping = role_mapping
        self._service = service

    @property
    def default_roles(self) -> DefaultRoles:
        return self._default_roles

    @property
    def role_mapping(self) -> RoleMapping:
        """The role mapping is done with the roles included in the ID Token sent by the authentication provider."""
        return self._role_mapping
