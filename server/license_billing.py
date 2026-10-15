"""Future payment adapter boundary. No payment is collected or simulated here."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ConfirmedRenewal:
    external_event_id: str
    subscription_id: str
    plan: str


class BillingVerifier(Protocol):
    def verify_authenticated_event(self, headers: dict, body: bytes) -> ConfirmedRenewal: ...
