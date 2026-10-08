import re
from db.connection import get_conn

async def list_tables() -> list[str]:
    async with get_conn() as conn:
        rows = await conn.fetch("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        return [r["table_name"] for r in rows]

async def describe_table(table_name: str) -> list[dict]:
    async with get_conn() as conn:
        rows = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = $1
            ORDER BY ordinal_position
        """, table_name)
        return [dict(r) for r in rows]

BLOCKED = {"drop", "delete", "insert", "update", "truncate",
           "alter", "create", "grant", "revoke"}

async def run_query(sql: str) -> list[dict]:
    cleaned = sql.strip().lower()
    if not cleaned.startswith("select"):
        raise ValueError("Only SELECT queries are allowed")

    found = set(re.findall(r"\b\w+\b", cleaned)) & BLOCKED
    if found:
        raise ValueError(f"Blocked keywords found: {sorted(found)}")

    async with get_conn() as conn:
        async with conn.transaction(readonly=True):
            rows = await conn.fetch(sql)
            return [dict(r) for r in rows[:100]]