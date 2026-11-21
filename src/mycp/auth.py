"""Static bearer-token auth (v1). Pure ASGI so it never buffers streamed responses."""

from __future__ import annotations

import secrets

from starlette.responses import JSONResponse

PROTECTED_PREFIXES = ("/mcp", "/api")


class BearerAuthMiddleware:
    def __init__(self, app, token: str, prefixes: tuple[str, ...] = PROTECTED_PREFIXES):
        self.app = app
        self.token = token
        self.prefixes = prefixes

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"].startswith(self.prefixes):
            headers = dict(scope["headers"])
            value = headers.get(b"authorization", b"").decode()
            supplied = value[7:] if value.lower().startswith("bearer ") else ""
            if not secrets.compare_digest(supplied.encode(), self.token.encode()):
                response = JSONResponse(
                    {"error": "unauthorized"},
                    status_code=401,
                    headers={"WWW-Authenticate": "Bearer"},
                )
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)
