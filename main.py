import os
import asyncpg
from fastapi import FastAPI
from pathlib import Path

DB_URL = os.environ.get("DATABASE_URL")  # ✅ use Render env var
SQL_DIR = Path("sql")

app = FastAPI(title="Ledger API")

# make sure these are imported correctly
# from routers import cards_router, profiles_router
# app.include_router(cards_router)
# app.include_router(profiles_router)

pool: asyncpg.Pool | None = None


async def run_sql_file(conn, filename: str):
    sql = (SQL_DIR / filename).read_text()
    await conn.execute(sql)


@app.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool(DB_URL)

    async with pool.acquire() as conn:
        await run_sql_file(conn, "01_schema.sql")
        await run_sql_file(conn, "02_seed.sql")


@app.on_event("shutdown")
async def shutdown():
    if pool:
        await pool.close()


@app.get("/")  # ✅ IMPORTANT health check route
async def root():
    return {"status": "ok"}


@app.post("/ledger")
async def ledger(account_id: str, amount: int):
    async with pool.acquire() as conn:
        sql = (SQL_DIR / "ledger.sql").read_text()
        row = await conn.fetchrow(sql, account_id, amount)
        return row["result"]

