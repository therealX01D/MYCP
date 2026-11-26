from ..scheme import RecordBase
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class RecordRead(RecordBase):
    id: int
    data: dict[str, Any]
    created_at: str
@dataclass(frozen=True)
class RecordCreate(RecordBase):
    data: dict[str, Any]
@dataclass(frozen=True)
class RecordQuery(RecordBase):
    text: str | None = None
    limit: int = 20
