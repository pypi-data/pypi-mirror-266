from __future__ import annotations

from collections.abc import Collection, Mapping, MutableMapping
from typing import Optional

from atoti_core import (
    DEPRECATED_WARNING_CATEGORY,
    ActiveViamClient,
    frozendict,
)
from typing_extensions import deprecated

from .._content_client import ContentClient
from ._column_key import ColumnKey
from ._restriction import Restriction
from ._restrictions import Restrictions
from ._roles import Role, Roles
from ._service import Service
from .basic_security import BasicSecurity
from .default_roles import DefaultRoles
from .individual_roles import IndividualRoles
from .kerberos_security import KerberosSecurity
from .ldap_security import LdapSecurity
from .oidc_security import OidcSecurity
from .role_mapping import RoleMapping


class Security:
    """Manage the parts of the security config that can be changed without restarting the :class:`~atoti.Session`.

    The roles and restrictions are stored in the :class:`user content storage <atoti.UserContentStorageConfig>`.
    Multiple sessions configured with the same user content storage will thus share their roles and restrictions.

    Note:
        Users without the :guilabel:`ROLE_USER` will not be able to access the application.
    """

    _service: Service

    def __init__(
        self,
        *,
        basic_credentials: Optional[MutableMapping[str, str]] = None,
        client: ActiveViamClient,
    ):
        if not client.has_atoti_python_api_endpoints:
            # Sessions started with the Java API ignore the restrictions and roles stored by Atoti Python API in the user content storage.
            # Managing security on such sessions is forbidden to avoid users being confused with their changes having no impact.
            raise RuntimeError(
                "Cannot manage security on a session that was not created with Atoti Python API."
            )

        self._basic_credentials = basic_credentials
        self._service = Service(client=ContentClient(client=client))

    @property
    def restrictions(self) -> MutableMapping[str, Restriction]:
        """Mapping from role name to corresponding restriction.

        There are reserved roles for which restrictions cannot be declared:

        * :guilabel:`ROLE_USER`: gives access the application
        * :guilabel:`ROLE_ADMIN`: gives full access (read, write, delete, etc) to the application

        The restrictions associated with a role can be modified at any time.

        * Restrictions apply on table columns and are inherited by all hierarchies based on these columns.
        * Restrictions on different hierarchies are intersected.
        * However, if a user has several roles with restrictions on the same hierarchies, access to the union of restricted elements will be granted.

        Example:
            .. doctest:: restrictions

                >>> df = pd.DataFrame(
                ...     [
                ...         ("Asia", "Korea", "KRW"),
                ...         ("Asia", "Japan", "JPY"),
                ...         ("Europe", "France", "EUR"),
                ...         ("Europe", "Germany", "EUR"),
                ...         ("Europe", "Norway", "NOK"),
                ...         ("Europe", "Sweden", "SEK"),
                ...     ],
                ...     columns=["Continent", "Country", "Currency"],
                ... )
                >>> session = tt.Session(authentication=tt.BasicAuthenticationConfig())
                >>> table = session.read_pandas(
                ...     df,
                ...     keys=["Continent", "Country", "Currency"],
                ...     table_name="Restrictions example",
                ... )
                >>> cube = session.create_cube(table)
                >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
                >>> cube.hierarchies["Geography"] = [
                ...     table["Continent"],
                ...     table["Country"],
                ... ]
                >>> for name in cube.hierarchies["Geography"].levels:
                ...     del cube.hierarchies[name]
                >>> username, password = "john", "abcdef123456"
                >>> user = session.security.basic.credentials[username] = password

            The user initially has no individual roles:

            .. doctest:: restrictions

                >>> username in session.security.individual_roles
                False

            Adding :guilabel:`ROLE_USER` to grant access to the application:

            .. doctest:: restrictions

                >>> session.security.individual_roles[username] = {"ROLE_USER"}

            Opening a query session to authenticate as the user just created:

            .. doctest:: restrictions

                >>> query_session = tt.QuerySession(
                ...     f"http://localhost:{session.port}",
                ...     auth=tt.BasicAuthentication(username=username, password=password),
                ... )
                >>> query_cube = query_session.cubes[cube.name]
                >>> l, m = query_cube.levels, query_cube.measures

            :guilabel:`ROLE_USER` has no restrictions so all the countries and currencies are accessible:

            .. doctest:: restrictions

                >>> query_cube.query(
                ...     m["contributors.COUNT"], levels=[l["Country"], l["Currency"]]
                ... )
                                           contributors.COUNT
                Continent Country Currency
                Asia      Japan   JPY                       1
                          Korea   KRW                       1
                Europe    France  EUR                       1
                          Germany EUR                       1
                          Norway  NOK                       1
                          Sweden  SEK                       1

            Adding a restricting role to the user so that only :guilabel:`France` is accessible:

            .. doctest:: restrictions

                >>> session.security.restrictions["ROLE_FRANCE"] = table["Country"] == "France"
                >>> session.security.individual_roles[username] |= {"ROLE_FRANCE"}
                >>> query_cube.query(m["contributors.COUNT"], levels=[l["Country"]])
                                  contributors.COUNT
                Continent Country
                Europe    France                   1

            Restrictions on the same hierarchy grant access to the union of the restricted elements:

            .. doctest:: restrictions

                >>> session.security.restrictions["ROLE_GERMANY"] = (
                ...     table["Country"] == "Germany"
                ... )
                >>> session.security.individual_roles[username] |= {"ROLE_GERMANY"}
                >>> query_cube.query(m["contributors.COUNT"], levels=[l["Country"]])
                                  contributors.COUNT
                Continent Country
                Europe    France                   1
                          Germany                  1

            Restrictions can grant access to multiple elements:

            .. doctest:: restrictions

                >>> session.security.restrictions["ROLE_NORDIC"] = table["Country"].isin(
                ...     "Norway", "Sweden"
                ... )
                >>> session.security.individual_roles[username] |= {"ROLE_NORDIC"}
                >>> query_cube.query(m["contributors.COUNT"], levels=[l["Country"]])
                                  contributors.COUNT
                Continent Country
                Europe    France                   1
                          Germany                  1
                          Norway                   1
                          Sweden                   1

            Also give access to the Asian countries with a restriction on :guilabel:`Continent`:

            .. doctest:: restrictions

                >>> session.security.restrictions["ROLE_ASIA"] = table["Continent"] == "Asia"
                >>> session.security.individual_roles[username] |= {"ROLE_ASIA"}
                >>> query_cube.query(m["contributors.COUNT"], levels=[l["Country"]])
                                  contributors.COUNT
                Continent Country
                Asia      Japan                    1
                          Korea                    1
                Europe    France                   1
                          Germany                  1
                          Norway                   1
                          Sweden                   1

            Restrictions on different hierarchies are intersected:

            .. doctest:: restrictions

                >>> session.security.restrictions["ROLE_EUR"] = table["Currency"] == "EUR"
                >>> session.security.individual_roles[username] |= {"ROLE_EUR"}
                >>> query_cube.query(
                ...     m["contributors.COUNT"], levels=[l["Country"], l["Currency"]]
                ... )
                                           contributors.COUNT
                Continent Country Currency
                Europe    France  EUR                       1
                          Germany EUR                       1

            Removing the roles granting access to :guilabel:`France` and :guilabel:`Germany` leaves no remaining accessible countries:

            .. doctest:: restrictions

                >>> session.security.individual_roles[username] -= {
                ...     "ROLE_FRANCE",
                ...     "ROLE_GERMANY",
                ... }
                >>> query_cube.query(m["contributors.COUNT"], levels=[l["Country"]])
                Empty DataFrame
                Columns: [contributors.COUNT]
                Index: []
        """
        return Restrictions(service=self._service)

    @property
    @deprecated(
        "Managing roles is deprecated. Use `Security.restrictions` instead.",
        category=DEPRECATED_WARNING_CATEGORY,
    )
    def roles(self) -> Roles:
        """Roles.

        :meta private:
        """
        return Roles(service=self._service)

    @property
    def individual_roles(self) -> IndividualRoles:
        return IndividualRoles(service=self._service)

    @property
    def basic(self) -> BasicSecurity:
        return BasicSecurity(
            credentials=self._basic_credentials,
            service=self._service,
        )

    @property
    def kerberos(self) -> KerberosSecurity:
        return KerberosSecurity(
            default_roles=DefaultRoles(
                authentication_type="KERBEROS",
                service=self._service,
            ),
            service=self._service,
        )

    @property
    def ldap(self) -> LdapSecurity:
        return LdapSecurity(
            default_roles=DefaultRoles(
                authentication_type="LDAP",
                service=self._service,
            ),
            role_mapping=RoleMapping(
                authentication_type="LDAP",
                service=self._service,
            ),
            service=self._service,
        )

    @property
    def oidc(self) -> OidcSecurity:
        return OidcSecurity(
            default_roles=DefaultRoles(
                authentication_type="OIDC",
                service=self._service,
            ),
            role_mapping=RoleMapping(
                authentication_type="OIDC",
                service=self._service,
            ),
            service=self._service,
        )

    def create_role(
        self,
        name: str,
        *,
        restrictions: Mapping[ColumnKey, Collection[str]] = frozendict(),
    ) -> Role:
        """Create a role with the given restrictions.

        :meta private:
        """
        role = Role(name, restrictions=restrictions, _service=self._service)
        self.roles[name] = role  # pyright: ignore[reportDeprecated]
        return role

    def _clear(self) -> None:
        if self._basic_credentials is not None:
            self._basic_credentials.clear()

        self._service.clear()
