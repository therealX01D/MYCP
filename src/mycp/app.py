"""One ASGI app: /mcp (MCP server) plus builder routes at / and /api."""

from __future__ import annotations

from mcp.server.transport_security import TransportSecuritySettings
from starlette.applications import Starlette

# from . import builder
from .auth import BearerAuthMiddleware
from .config import Settings
from .registry import RecordStore
from .server import build_server


def create_app(settings: Settings, store: RecordStore, *, with_builder: bool = True) -> Starlette:
    mcp = build_server(store)

    # DNS-rebinding protection: accept localhost plus anything in MYCP_ALLOWED_HOSTS.
    hosts = ["localhost:*", "127.0.0.1:*", "[::1]:*", *settings.allowed_hosts]
    origins = [f"http://{h}" for h in hosts]
    security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=hosts,
        allowed_origins=origins,
    )

    # Start from the MCP app so its lifespan (session manager) keeps running,
    # then attach the builder routes to the same app.
    app = mcp.streamable_http_app(host=settings.host, transport_security=security)
    # if with_builder:
    #     # app.router.routes.extend(builder.routes())
    # else:
    #     app.router.routes.extend(r for r in builder.routes() if r.path == "/healthz")
    app.add_middleware(BearerAuthMiddleware, token=settings.token)
    return app
