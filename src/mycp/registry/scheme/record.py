from dataclasses import dataclass
from typing import Any

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
