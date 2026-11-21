"""Settings, read from environment variables (see .env.example)."""

from __future__ import annotations

import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path


def _load_dotenv(path: Path = Path(".env")) -> None:
    """Tiny .env loader so `mycp run` works outside Docker. Real env vars win."""
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Settings:
    db_path: Path
    host: str = "127.0.0.1"
    port: int = 8080
    token: str = ""
    allowed_hosts: list[str] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "Settings":
        _load_dotenv()
        db_path = Path(os.environ.get("MYCP_DB_PATH") or "./data/mycp.db").expanduser()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        extra_hosts = [
            h.strip()
            for h in (os.environ.get("MYCP_ALLOWED_HOSTS") or "").split(",")
            if h.strip()
        ]
        return cls(
            db_path=db_path,
            host=os.environ.get("MYCP_HOST") or "127.0.0.1",
            port=int(os.environ.get("MYCP_PORT") or 8080),
            token=os.environ.get("MYCP_TOKEN") or _load_or_create_token(db_path.parent),
            allowed_hosts=extra_hosts,
        )


def _load_or_create_token(directory: Path) -> str:
    """Single static bearer token, generated on first run (v1 auth model)."""
    token_file = directory / "token"
    if token_file.is_file():
        return token_file.read_text().strip()
    token = secrets.token_urlsafe(32)
    token_file.write_text(token + "\n")
    token_file.chmod(0o600)
    return token
