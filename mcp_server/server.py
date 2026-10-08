import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp.server.fastmcp import FastMCP
from db.tools import list_tables, describe_table, run_query

mcp = FastMCP("DB Tool")

@mcp.tool()
async def get_tables() -> list[str]:
    """List all tables in the database."""
    return await list_tables()

@mcp.tool()
async def get_table_schema(table_name: str) -> list[dict]:
    """Get column names and types for a table. Call this before writing a query."""
    return await describe_table(table_name)

@mcp.tool()
async def query_database(sql: str) -> list[dict]:
    """Run a read-only SELECT query (max 100 rows)."""
    return await run_query(sql)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.transport == "http":
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="streamable-http")  # served at http://host:port/mcp
    else:
        mcp.run(transport="stdio")