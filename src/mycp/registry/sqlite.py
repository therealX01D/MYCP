"""SQLite implementation of the storage interfaces.

One connection for the life of the store, guarded by a lock. Pragmas are set once.
Fine for a single-user server; the hosted edition swaps in Postgres behind the
same interface.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .base import RecordInput,RecordReturn,RecordQuery,RecordStore,DBConfig
from dataclasses import dataclass

SCHEMA = """
CREATE TABLE IF NOT EXISTS records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT NOT NULL,
    collection  TEXT NOT NULL,
    data        TEXT NOT NULL,
    created_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_records_user_collection
    ON records (user_id, collection, id DESC);
"""


def _escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

@dataclass(frozen=True, kw_only=True)
class SQLiteConfig(DBConfig):
    filepath: Path | str

    def connection_summary(self) -> str:
        return f"sqlite:///{self.filepath}"

class SQLiteRecordStore(RecordStore):
    def __init__(self, config:SQLiteConfig):
        self.path = str(config.filepath)
        # The server may call us from different threads; the lock serialises access.
        self._conn = sqlite3.connect(self.path, check_same_thread=False, timeout=10)
        self._lock = threading.Lock()
        self._conn.execute("PRAGMA journal_mode=WAL")    # persistent, set once
        self._conn.execute("PRAGMA synchronous=NORMAL")  # safe with WAL, faster
        self._conn.execute("PRAGMA busy_timeout=10000")
        self._conn.executescript(SCHEMA)

    def append(self, obj:RecordInput) -> RecordReturn:
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._lock, self._conn:  # `with conn` commits, or rolls back on error
            cur = self._conn.execute(
                "INSERT INTO records (user_id, collection, data, created_at) "
                "VALUES (?, ?, ?, ?)",
                (obj.user_id, obj.collection, json.dumps(obj.data), created_at),
            )
            return RecordReturn(cur.lastrowid, obj.collection, obj.user_id, obj.data, created_at)

    def query(
        self,
        obj:RecordQuery
    ) -> list[RecordReturn]:
        sql = "SELECT id, collection, data, created_at FROM records WHERE user_id = ? AND collection = ?"
        params: list[Any] = [obj.user_id, obj.collection]
        if obj.text:
            sql += " AND data LIKE ? ESCAPE '\\'"
            params.append(f"%{_escape_like(obj.text)}%")
        sql += " ORDER BY id DESC LIMIT ?"
        params.append(max(1, min(obj.limit, 200)))
        with self._lock:
            rows = self._conn.execute(sql, params).fetchall()  # fetch inside the lock
        return [RecordReturn(r[0], r[1], obj.user_id, json.loads(r[2]), r[3]) for r in rows]

    def close(self) -> None:
        """Checkpoint the WAL and close. Safe to call more than once."""
        with self._lock:
            try:
                self._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                self._conn.close()
            except sqlite3.ProgrammingError:
                pass  # already closed
