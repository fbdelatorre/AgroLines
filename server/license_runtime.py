"""Production factory, private inputs provided only to the independent server process."""

import os

from server.config import Settings
from server.license_app import create_app
from server.license_service import Issuer


def application():
    required = [
        "AGROLINES_DATABASE_URL",
        "AGROLINES_LICENSE_KID",
        "AGROLINES_LICENSE_SIGNING_FILE",
        "AGROLINES_LICENSE_WRAPPING_FILE",
    ]
    if any(not os.getenv(name) for name in required):
        raise RuntimeError(
            "Configure banco PostgreSQL e arquivos de chaves do servidor de licenças."
        )
    settings = Settings()
    if not settings.database_url.get_secret_value().startswith("postgresql+psycopg://"):
        raise RuntimeError("Implantação do serviço exige PostgreSQL; SQLite é somente laboratório.")
    issuer = Issuer.from_files(
        os.environ[required[1]], os.environ[required[2]], os.environ[required[3]]
    )
    return create_app(issuer, settings)
