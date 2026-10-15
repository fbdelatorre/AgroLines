"""Offline-valid signed licenses. DPAPI vault and independent anchor are injected."""

import time
from functools import wraps
from threading import RLock
from uuid import UUID, uuid4

from core.license_protocol import verify
from core.licensing import Entitlements, Module

RECOVERY = frozenset({Module.PROJECTS, Module.BACKUP})


def synchronized(method):
    @wraps(method)
    def call(self, *args, **kwargs):
        with self.lock:
            return method(self, *args, **kwargs)

    return call


class LicenseManager:
    def __init__(self, vault, anchor, keyring, transport, clock=time.time):
        self.lock = RLock()
        self.vault, self.anchor, self.keyring, self.transport = vault, anchor, keyring, transport
        self.clock = clock
        self.error = ""
        self.state = vault.load()
        saved_anchor = anchor.load()
        if self.state is None:
            if saved_anchor:
                raise ValueError("Registro de ativação incompleto; restaure ou contate o suporte.")
            self.state = {"installation_id": str(uuid4()), "license": None, "credential": None}
            self._persist()
        if not saved_anchor and self.state.get("license"):
            raise ValueError("Registro protegido ausente; contate o suporte.")
        try:
            if str(UUID(self.state["installation_id"])) != self.state["installation_id"]:
                raise ValueError("Identidade de instalação inválida.")
        except (KeyError, TypeError, AttributeError) as exc:
            raise ValueError("Registro de instalação inválido.") from exc
        if not saved_anchor:
            saved_anchor = {
                "installation_id": self.state["installation_id"],
                "max_time": 0,
                "generations": {},
                "revoked": [],
            }
        if (
            not isinstance(saved_anchor, dict)
            or not isinstance(saved_anchor.get("generations"), dict)
            or not isinstance(saved_anchor.get("revoked"), list)
            or type(saved_anchor.get("max_time")) is not int
        ):
            raise ValueError("Registro protegido de licença inválido.")
        if any(type(v) is not int or v < 0 for v in saved_anchor["generations"].values()):
            raise ValueError("Revisões protegidas inválidas.")
        if saved_anchor.get("installation_id") != self.state["installation_id"]:
            raise ValueError("Identidade protegida da instalação divergente.")
        self.guard = saved_anchor
        self._record_time()

    def _persist(self):
        if not self.vault.save(self.state):
            raise OSError("Não foi possível proteger a licença com DPAPI.")

    def _record_time(self):
        now = int(self.clock())
        self.rollback = now + 300 < self.guard["max_time"]
        self.guard["max_time"] = max(now, self.guard["max_time"])
        if not self.anchor.save(self.guard):
            raise OSError("Não foi possível preservar o registro protegido de licença.")

    @synchronized
    def parsed(self):
        envelope = self.state.get("license")
        return verify(envelope, self.keyring, self.state["installation_id"]) if envelope else None

    @synchronized
    def verify(self):
        reason = "Ative sua assinatura. Projetos existentes continuam acessíveis para recuperação."
        try:
            self._record_time()
            value = self.parsed()
            if value:
                identifier = value["activation_id"]
                if identifier in self.guard["revoked"] or value["status"] == "revoked":
                    reason = "Ativação revogada. Consulte o suporte."
                elif value["status"] == "suspended":
                    reason = "Assinatura suspensa. Consulte o suporte."
                elif value["generation"] < self.guard["generations"].get(identifier, 0):
                    reason = "Registro antigo de licença recusado."
                elif self.rollback or value["issued_at"] > int(self.clock()) + 300:
                    reason = "Relógio inconsistente. Corrija a data e verifique sua licença."
                elif value["expires_at"] <= int(self.clock()):
                    reason = "Assinatura vencida. Renove para iniciar novas edições."
                else:
                    return Entitlements(
                        value["edition"],
                        frozenset({Module.PROJECTS, Module.GEOMETRY, Module.BACKUP}),
                        True,
                        "Ativa",
                    )
        except (ValueError, OSError, KeyError, TypeError):
            reason = "Licença local inválida ou armazenamento protegido indisponível."
        return Entitlements("recovery", RECOVERY, True, reason, read_only=True)

    @synchronized
    def accept(self, result, authoritative=False):
        if not isinstance(result, dict) or "license" not in result:
            raise ValueError("Resposta de licenciamento inválida.")
        if "credential" in result and (
            not isinstance(result["credential"], str) or not 30 <= len(result["credential"]) <= 100
        ):
            raise ValueError("Credencial de instalação inválida.")
        devices = result.get("devices", [])
        if (
            not isinstance(devices, list)
            or len(devices) > 2
            or any(
                not isinstance(row, dict)
                or row.get("slot") not in (1, 2)
                or (
                    row.get("label") is not None
                    and (not isinstance(row["label"], str) or len(row["label"]) > 80)
                )
                for row in devices
            )
        ):
            raise ValueError("Lista de computadores inválida.")
        value = verify(result["license"], self.keyring, self.state["installation_id"])
        identifier, generation = value["activation_id"], value["generation"]
        if generation < self.guard["generations"].get(identifier, 0):
            raise ValueError("Resposta de licença antiga recusada.")
        if value["issued_at"] > int(self.clock()) + 300:
            raise ValueError("Ajuste o relógio antes de aceitar a licença.")
        if identifier in self.guard["revoked"] and value["status"] == "active":
            raise ValueError("Ativação revogada exige uma nova vaga autorizada.")
        if (
            authoritative
            and generation > self.guard["generations"].get(identifier, 0)
            and abs(value["issued_at"] - int(self.clock())) <= 300
        ):
            # A fresh HTTPS response with a newer server revision permits recovery
            # after a legitimate correction of a previously advanced local clock.
            self.guard["max_time"] = int(self.clock())
        if value["status"] == "revoked" and identifier not in self.guard["revoked"]:
            self.guard["revoked"].append(identifier)
        self.guard["generations"][identifier] = generation
        # Revocation/high-water mark saved independently BEFORE the replaceable license file.
        self._record_time()
        self.state["license"] = result["license"]
        if "credential" in result:
            self.state["credential"] = result["credential"]
        self.state["devices"] = result.get("devices", [])
        self.state["last_verified"] = value["issued_at"]
        self._persist()
        self.error = ""
        return value

    def activate(self, email, key, label):
        return self.accept(
            self.transport.post(
                "activate",
                {
                    "email": email,
                    "key": key,
                    "label": label,
                    "installation_id": self.state["installation_id"],
                },
            ),
            authoritative=True,
        )

    def check(self, deactivate=False):
        value = self.parsed()
        if not value or not self.state.get("credential"):
            raise ValueError("Ative este computador primeiro.")
        try:
            result = self.transport.post(
                "deactivate" if deactivate else "check",
                {
                    "activation_id": value["activation_id"],
                    "installation_id": self.state["installation_id"],
                    "credential": self.state["credential"],
                },
            )
            return self.accept(result, authoritative=True)
        except (OSError, TimeoutError, ValueError) as exc:
            self.error = "Não foi possível verificar agora. A validade local foi preservada."
            raise OSError(self.error) from exc


class RecoveryManager:
    """Damaged licensing storage never makes agricultural files inaccessible."""

    def __init__(self, reason):
        self.state = {"license": None, "credential": None}
        self.reason = "Ativação protegida requer suporte. " + str(reason)

    def verify(self):
        return Entitlements("recovery", RECOVERY, True, self.reason, read_only=True)

    def parsed(self):
        return None

    def activate(self, *args):
        raise ValueError(self.reason)

    def check(self, *args, **kwargs):
        raise ValueError(self.reason)
