from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Producer:
    id: UUID
    name: str


@dataclass(frozen=True, slots=True)
class Farm:
    id: UUID
    producer_id: UUID
    name: str


@dataclass(frozen=True, slots=True)
class Field:
    id: UUID
    farm_id: UUID
    name: str
    boundary_version: int = 1
