"""The MCP server.

Milestone 1: two hardcoded tools (remember, recall) and one resource (notes).
Milestone 2 replaces the hardcoded tools with specs loaded from the registry.
"""

from __future__ import annotations

from mcp.server import MCPServer

from ..identity import current_user
from ..registry import RecordStore

NOTES = "notes"


def _format(records) -> str:
    return "\n".join(f"[{r.id}] {r.created_at}  {r.data.get('text', '')}" for r in records)


def build_server(store: RecordStore) -> MCPServer:
    mcp = MCPServer(
        "mycp",
        instructions=(
            "Personal memory server. Use `remember` to save anything the user wants "
            "kept, and `recall` to look things up before answering questions about them."
        ),
    )

    @mcp.tool()
    def remember(text: str) -> str:
        """Save a note about the user. Use when the user asks you to remember
        something or states a lasting fact or preference."""
        record = store.append(current_user(), NOTES, {"text": text})
        return f"Saved note #{record.id}."

    @mcp.tool()
    def recall(query: str = "", limit: int = 10) -> str:
        """Search saved notes (newest first). Leave query empty to list recent notes."""
        records = store.query(current_user(), NOTES, text=query or None, limit=limit)
        return _format(records) if records else "No matching notes."

    @mcp.resource("mycp://notes", name="notes", mime_type="text/plain",
                  description="The most recent saved notes.")
    def notes() -> str:
        records = store.query(current_user(), NOTES, limit=50)
        return _format(records) if records else "No notes yet."

    return mcp
