# MYCP

**A self-hosted chatbot that builds your personal MCP server as you talk to it.**

Tell it what you want to track or do ("log my workouts", "keep a reading list", "save my meeting notes"), and it creates the matching tools and stores the data. Every MCP client you use (Claude Desktop, Cursor, claude.ai custom connectors, and others) gets those tools immediately, with no code written by you.

> **Status: early development.** The commands below describe the target experience. See the [Roadmap](#roadmap) for what is built.

---

## How it works

```
 You ⇄ Builder chat (LLM + meta-tools)
              │  writes tool specs and data
              ▼
      Registry (SQLite): tools, resources, prompts, records
              │  read at runtime
              ▼
   MCP server  ⇄  Your MCP clients (Claude Desktop, Cursor, ...)
```

1. You chat with the **builder**. When it sees a new need, it proposes a tool.
2. You **approve** it. The tool spec is saved to the registry.
3. The **MCP server** reads the registry on every request, so the new tool is available at once. Connected clients are notified with `notifications/tools/list_changed`.
4. Your data lives in a local SQLite file that you own.

## Features

- **Self-hosted and local-first.** One process, one SQLite file, no cloud dependency beyond the LLM you choose.
- **Tools grow from conversation.** Describe a need and get a tool, with approval before anything changes.
- **Declarative tools, not arbitrary code.** Tools are JSON specs executed by a small set of safe handlers (see below).
- **Versioned registry.** Every tool change is stored, so you can roll back.
- **Standard MCP.** Streamable HTTP (and stdio for local clients), so any MCP client can connect.
- **Portable.** Export your whole server (tools plus data) as a single file.
- **Pluggable LLM provider.** Use the Anthropic API by default, or bring your own.

### Tool specs

A tool is a description plus a handler:

```json
{
  "name": "log_workout",
  "description": "Log a workout session. Use when the user reports exercise.",
  "input_schema": {
    "type": "object",
    "properties": {
      "type": { "type": "string" },
      "minutes": { "type": "number" }
    },
    "required": ["type"]
  },
  "handler": { "kind": "append_record", "collection": "workouts" }
}
```

Built-in handler kinds:

| Handler | What it does |
|---|---|
| `append_record` | Adds a record to a collection |
| `query_records` | Searches and filters a collection |
| `update_record` | Modifies an existing record |
| `http_call` | Calls an allowlisted URL from a template |
| `prompt_template` | Returns a reusable prompt |

## Quick start

> Target experience. Commands may change as the project is built.

**Requirements:** Docker, plus an API key for your LLM provider.

```bash
git clone https://github.com/<you>/mycp.git
cd mycp
cp .env.example .env        # add your LLM API key
docker compose up
```

Then:

1. Open `http://localhost:8080` and start chatting with the builder.
2. Copy the bearer token printed on first run.
3. Connect your MCP client to `http://localhost:8080/mcp` using that token.

### Connecting a client

Clients that support remote MCP servers can use the URL and token directly. For clients that only support stdio, run the server in stdio mode and point the client's config at the command. Exact snippets will be added once the CLI is finalized.

## Project layout (planned)

```
mycp/
├── server/        # MCP server: reads the registry, runs handlers
├── builder/       # Builder chat: LLM loop and meta-tools
├── registry/      # Storage interfaces and SQLite implementation
├── handlers/      # append_record, query_records, ...
├── web/           # Minimal chat UI
└── docker-compose.yml
```

The builder and the server are separate modules that share only the registry.

## Security model

- **Approval first.** The builder proposes tool changes and nothing is applied until you approve.
- **No generated code in v1.** Handlers are a fixed, reviewed set.
- **Outbound calls are allowlisted.** `http_call` can only reach hosts you configure.
- **Single bearer token.** Generated on first run. If you expose the server to the internet, put it behind a reverse proxy with TLS.
- **Treat tool output as untrusted.** Data returned through tools can contain prompt injection, so review what your clients do with it.
- **Secrets stay out of specs.** Keep API keys in environment variables, not in tool definitions.

## Roadmap

- [x] **1. Skeleton:** MCP server with hardcoded `remember` and `recall` tools and a notes resource, working in Claude Desktop
- [ ] **2. Registry:** SQLite tables for tool specs, records and versions, with `append_record` and `query_records`
- [ ] **3. Builder loop:** chat UI with `create_tool`, `update_tool` and `list_tools`, an approval card, and `list_changed` notifications
- [ ] **4. Safety and polish:** versioning and rollback, a tool-count cap, schema validation, export and import
- [ ] **5. Launch:** docs, demo, example tool packs
- [ ] **Later:** sandboxed code tools, more handler kinds, hosted multi-user edition

## Design principles

- **Start simple.** One process, one file, one user.
- **Keep the seams.** Every table has a `user_id` (always `default` in v1), storage sits behind interfaces, and the current user is resolved in one function, so multi-user support can be added without a rewrite.
- **Few, well-described tools.** Tool descriptions drive how well a client model uses them, and too many tools hurt selection, so the builder merges near-duplicates and enforces a cap.

## Open source and hosted edition

The self-hosted, single-user version is and will remain open source. A hosted edition with multi-user accounts, OAuth, managed hosting, backups and sync is planned as a paid option.

## Contributing

Contributions are welcome once the skeleton lands. Until then, issues and design feedback are the most useful thing to open.

## License

To be decided before the first public commit. Permissive options (Apache-2.0, MIT) maximize adoption, while AGPL-3.0 discourages reselling the code as a hosted service.
