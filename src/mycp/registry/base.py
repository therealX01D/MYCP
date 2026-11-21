"""Storage interfaces.

Everything else in MYCP depends on these protocols, never on SQLite directly,
so the hosted edition can swap in Postgres without touching the server or builder.

Milestone 2 adds a `ToolRegistry` protocol here (tool specs, versions, rollback).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class Record:
    id: int
    collection: str
    data: dict[str, Any]
    created_at: str


class RecordStore(Protocol):
    def append(self, user_id: str, collection: str, data: dict[str, Any]) -> Record:
        """Add a record to a collection and return it."""
        ...

    def query(
        self,
        user_id: str,
        collection: str,
        text: str | None = None,
        limit: int = 20,
    ) -> list[Record]:
        """Newest-first records in a collection, optionally filtered by text."""
        ...

    def close(self) -> None:
        """Release resources. Called once on shutdown."""
        ...


