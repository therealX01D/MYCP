from dataclasses import dataclass
from .base  import BaseModel
@dataclass(frozen=True)
class RecordBase(BaseModel):
    collection: str
    user_id: str
