"""Storage interfaces.

Everything else in MYCP depends on these protocols, never on SQLite directly,
so the hosted edition can swap in Postgres without touching the server or builder.

Milestone 2 adds a `ToolRegistry` protocol here (tool specs, versions, rollback).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol
from abc import ABC, abstractmethod

@dataclass(frozen=True)
class RecordReturn:
    id: int
    collection: str
    user_id: str
    data: dict[str, Any]
    created_at: str
@dataclass(frozen=True)
class RecordInput:
    collection: str
    user_id: str
    data: dict[str, Any]
@dataclass(frozen=True)
class RecordQuery:
    collection: str
    user_id: str
    text: str | None = None
    limit: int = 20

@dataclass(frozen=True, kw_only=True)
class DBConfig(ABC):
    """Abstract base config shared by all databases."""
    timeout: float = 10.0

    @abstractmethod
    def connection_summary(self) -> str:
        ...

class RecordStore(Protocol):
    def __init__(self,config: DBConfig): ...
    def append(self, obj: RecordInput) -> RecordReturn:
        """Add a record to a collection and return it."""
        ...
    def query(self,query:RecordQuery) -> list[RecordReturn]:
        """Newest-first records in a collection, optionally filtered by text."""
        ...
    def close(self) -> None:
        """Release resources. Called once on shutdown."""
        ...


