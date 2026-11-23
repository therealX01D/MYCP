"""`mycp` command line.

  mycp run     MCP server + builder together (default)
  mycp serve   MCP server only
  mycp chat    builder only (milestone 3)
  mycp stdio   MCP server over stdio, for clients like Claude Desktop
  mycp token   print the bearer token
"""

from __future__ import annotations

import argparse
import sys

from .config import Settings
from .registry import SQLiteRecordStore,SQLiteConfig


def _serve(settings: Settings, *, with_builder: bool) -> None:
    import uvicorn

    from .app import create_app
    config = SQLiteConfig(filepath=settings.db_path)
    store = SQLiteRecordStore(config=config)
    app = create_app(settings, store, with_builder=with_builder)
    print(f"MYCP listening on http://{settings.host}:{settings.port}  (MCP endpoint: /mcp)")
    print(f"Bearer token: {settings.token}")
    try:
        uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")
    finally:
        store.close()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="mycp", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", default="run",
                        choices=["run", "serve", "chat", "stdio", "token"])
    parser.add_argument("--host", help="override MYCP_HOST")
    parser.add_argument("--port", type=int, help="override MYCP_PORT")
    args = parser.parse_args(argv)

    settings = Settings.from_env()
    if args.host or args.port:
        from dataclasses import replace
        settings = replace(settings, host=args.host or settings.host,
                           port=args.port or settings.port)

    if args.command == "run":
        _serve(settings, with_builder=True)
    elif args.command == "serve":
        _serve(settings, with_builder=False)
    elif args.command == "chat":
        sys.exit("The builder chat is not implemented yet (milestone 3).")
    elif args.command == "stdio":
        from .server import build_server
        store = SQLiteRecordStore(SQLiteConfig(settings.db_path))
        try:
            build_server(store).run("stdio")
        finally:
            store.close()
    elif args.command == "token":
        print(settings.token)


if __name__ == "__main__":
    main()
