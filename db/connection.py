import asyncpg
from contextlib import asynccontextmanager
from settings.setting import Settings

settings = Settings()
_pool: asyncpg.Pool | None = None

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            host=settings.db_host, port=settings.db_port,
            user=settings.db_user, password=settings.db_password,
            database=settings.db_name,
            min_size=2, max_size=10,
            command_timeout=30,   # kill runaway queries
        )
    return _pool

@asynccontextmanager
async def get_conn():
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn