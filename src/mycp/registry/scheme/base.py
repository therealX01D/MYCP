from dataclasses import dataclass
@dataclass(frozen=True)
class BaseModel:
    id: int