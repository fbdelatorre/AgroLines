"""Local entitlement boundary; issuance and commercial activation are intentionally absent."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class Module(StrEnum):
    PROJECTS = "projects"
    GEOMETRY = "geometry"
    BACKUP = "backup"
    COLLABORATION = "collaboration"


@dataclass(frozen=True)
class Entitlements:
    edition: str
    modules: frozenset[Module]
    valid: bool
    reason: str
    read_only: bool = False

    def permits(self, module: Module) -> bool:
        return self.valid and module in self.modules


class LicenseVerifier(Protocol):
    """Must verify locally. Never use entitlements as remote sharing authorization."""

    def verify(self) -> Entitlements: ...


class DevelopmentLicense:
    def verify(self) -> Entitlements:
        return Entitlements("development", frozenset(Module), True, "Desenvolvimento sem licença")


class PublicSignatureVerifier(Protocol):
    """Future adapter accepts issuer public keys only; rejects unknown key/algorithm.

    Verify exact signed payload bytes before parsing claims (expiry, modules, edition,
    installation scope). Private issuance keys belong exclusively to the issuer.
    No network heartbeat or hardware collection is part of this contract.
    """

    def verify(self, payload: bytes, signature: bytes, key_id: str, algorithm: str) -> bool: ...


class Edition(StrEnum):
    INDIVIDUAL = "individual"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


# Future commercial policy: edition defaults, further intersected with signed modules.
# DevelopmentLicense deliberately remains independent of this provisional catalog.
EDITION_MODULES = {
    Edition.INDIVIDUAL: frozenset({Module.PROJECTS, Module.GEOMETRY, Module.BACKUP}),
    Edition.PROFESSIONAL: frozenset(Module),
    Edition.ENTERPRISE: frozenset(Module),
}
