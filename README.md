# llm-db-tool

A read-only [MCP](https://modelcontextprotocol.io) server that lets AI clients (Claude Code, Claude Desktop, GitHub Copilot, Cursor) query a PostgreSQL database in plain English.

```
AI client  ──stdio──▶  MCP server (Python)  ──asyncpg──▶  PostgreSQL
```

## Tools

| Tool | Description |
|---|---|
| `get_tables` | List tables in the `public` schema |
| `get_table_schema` | Show columns, types and nullability for a table |
| `query_database` | Run a read-only `SELECT` (max 100 rows) |

## Safety

1. Only statements starting with `SELECT` are accepted
2. Dangerous keywords (`drop`, `delete`, `insert`, `update`, ...) are blocked
3. Queries run inside a read-only Postgres transaction
4. Results are capped at 100 rows, with a 30 second command timeout

Keyword filters are a seatbelt, not a wall. Connect with a dedicated read-only database user:

```sql
CREATE ROLE mcp_readonly LOGIN PASSWORD 'change-me';
GRANT CONNECT ON DATABASE mydb TO mcp_readonly;
GRANT USAGE ON SCHEMA public TO mcp_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO mcp_readonly;
```

## Setup

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

Create a `.env` file (already in `.gitignore`):

```
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=mcp_readonly
DB_PASSWORD=change-me
DB_NAME=mydb
```

## Run and test

Open the MCP Inspector to call each tool by hand:

```bash
uv run mcp dev mcp_server/server.py
```

## Connect a client

**Claude Code**

```bash
claude mcp add db-tool -- uv run --directory /absolute/path/to/this/folder mcp_server/server.py
```

**Claude Desktop** (`claude_desktop_config.json`) or a project `.mcp.json`:

```json
{
  "mcpServers": {
    "db-tool": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/this/folder", "mcp_server/server.py"]
    }
  }
}
```

**VS Code Copilot** (`.vscode/mcp.json`, use `"servers"` instead of `"mcpServers"` and add `"type": "stdio"`).

Then ask something like: *"List the tables in my database and show the 5 most recent rows from the biggest one."*

## Project layout

```
├── .env                  # DB credentials (not committed)
├── settings/setting.py   # pydantic-settings config
├── db/connection.py      # asyncpg connection pool
├── db/tools.py           # list_tables, describe_table, run_query
└── mcp_server/server.py  # FastMCP tool definitions
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `Connect call failed ... 5432` | Postgres isn't reachable at `DB_HOST`. Check it is running (`pg_isready`), the IP is current, then restart the MCP server. |
| Server won't start | Verify the path in your MCP config and run the command by hand first. |
| Garbled or failing connection | Never `print()` in the server. stdout is the protocol channel, so use `logging`. |
| Tools don't appear | Restart the client, and in VS Code use Agent mode. |
