from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import BaseRoute, Route


async def healthz(request: Request) -> JSONResponse:
    """Public health check endpoint."""
    return JSONResponse({"ok": True})


def get_builder_routes() -> list[BaseRoute]:
    """Return all routes owned by the builder submodule."""
    return [
        Route("/healthz", healthz, methods=["GET"]),
    ]
