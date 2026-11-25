from typing import Any

from ..identity import current_user
from ..registry import RecordInput, RecordReturn, RecordStore


def append_record(collection: str, json: dict[str, Any], recordStore: RecordStore) -> RecordReturn:
    return recordStore.append(RecordInput(collection, current_user(), json))
