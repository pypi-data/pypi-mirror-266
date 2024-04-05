from pathlib import Path
from typing import Optional

from atoti_core import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, keyword_only_dataclass
from pydantic.dataclasses import dataclass


@keyword_only_dataclass
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class ClientCertificate:
    """A client certificate to open a :class:`atoti_query.QuerySession` against a session configured with :class:`atoti.ClientCertificateConfig`.

    Example:
        .. doctest:: client_certificate
            :hide:

            >>> CERTIFICATES_DIRECTORY = (
            ...     _PYTHON_PACKAGES_PATH
            ...     / "atoti"
            ...     / "tests_atoti"
            ...     / "resources"
            ...     / "config"
            ...     / "certificates"
            ... )
            >>> session = tt.Session(
            ...     client_certificate=tt.ClientCertificateConfig(
            ...         trust_store=CERTIFICATES_DIRECTORY / "truststore.jks",
            ...         trust_store_password="changeit",
            ...     ),
            ...     https=tt.HttpsConfig(
            ...         certificate=CERTIFICATES_DIRECTORY / "localhost.p12",
            ...         password="changeit",
            ...     ),
            ... )

        .. doctest:: client_certificate

            >>> client_certificate = tt.ClientCertificate(
            ...     certificate=CERTIFICATES_DIRECTORY / "client.pem",
            ...     keyfile=CERTIFICATES_DIRECTORY / "client.key",
            ... )
            >>> query_session = tt.QuerySession(
            ...     f"https://localhost:{session.port}",
            ...     certificate_authority=CERTIFICATES_DIRECTORY / "root-CA.crt",
            ...     client_certificate=client_certificate,
            ... )
    """

    certificate: Path
    """Path to the ``.pem`` file containing the client certificate."""

    keyfile: Optional[Path] = None
    """Path to the certificate ``.key`` file."""

    password: Optional[str] = None
    """The certificate password."""
