"""Boots the real app with uvicorn and talks to it with a real MCP client."""

import socket
import threading
import time
from dataclasses import replace

import httpx
import pytest
import uvicorn
from mcp.client import Client
from mcp.client.streamable_http import create_mcp_http_client, streamable_http_client

from mycp.app import create_app
from mycp.config import Settings
from mycp.registry import SQLiteRecordStore,SQLiteConfig

TOKEN = "test-token"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def base_url(tmp_path):
    port = _free_port()
    settings = Settings(db_path=tmp_path / "e2e.db", port=port, token=TOKEN)
    store = SQLiteRecordStore(SQLiteConfig(filepath=settings.db_path))
    app = create_app(settings, store)
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=5)
    store.close()


def _client(base_url: str, token: str = TOKEN) -> Client:
    http = create_mcp_http_client(headers={"Authorization": f"Bearer {token}"})
    return Client(streamable_http_client(f"{base_url}/mcp", http_client=http))


def test_healthz_is_public_and_mcp_requires_token(base_url):
    assert httpx.get(f"{base_url}/healthz").json()["ok"] is True
    assert httpx.post(f"{base_url}/mcp", json={}).status_code == 401
    wrong = httpx.post(f"{base_url}/mcp", json={}, headers={"Authorization": "Bearer nope"})
    assert wrong.status_code == 401


async def test_remember_then_recall_and_resource(base_url):
    async with _client(base_url) as client:
        tools = await client.list_tools()
        assert {t.name for t in tools.tools} >= {"remember", "recall"}

        saved = await client.call_tool("remember", {"text": "I prefer dark mode"})
        assert "Saved note" in saved.content[0].text

        found = await client.call_tool("recall", {"query": "dark"})
        assert "dark mode" in found.content[0].text

        resources = await client.list_resources()
        assert any(str(r.uri) == "mycp://notes" for r in resources.resources)
        notes = await client.read_resource("mycp://notes")
        assert "dark mode" in notes.contents[0].text
