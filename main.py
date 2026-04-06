import os
import uvicorn
import asyncpg
from fastapi import FastAPI
from pathlib import Path


DB_URL = os.environ.get("DATABASE_URL")  # ✅ use Render env var
BASE_DIR = Path(__file__).resolve().parent
SQL_DIR = BASE_DIR / "sql"

app = FastAPI(title="Ledger API")

# make sure these are imported correctly
# from routers import cards_router, profiles_router
# app.include_router(cards_router)
# app.include_router(profiles_router)

pool: asyncpg.Pool | None = None


async def run_sql_file(conn, filename: str,expect_result=False):
    sql = (SQL_DIR / filename).read_text()
    if expect_result:
        return await conn.fetchrow(sql)
    else:
        await conn.execute(sql)

@app.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool(DB_URL)

    async with pool.acquire() as conn:
        await run_sql_file(conn, "create_wallet_schema.sql")
        await run_sql_file(conn, "Seed_wallet.sql")



@app.on_event("shutdown")
async def shutdown():
    if pool:
        await pool.close()


@app.get("/")  # ✅ IMPORTANT health check route
async def root():
    return {"status": "ok"}


@app.post("/ledger")
async def post_ledger(account_id: str, amount: int):
    async with pool.acquire() as conn:
        sql = (SQL_DIR / "Wallet_debit.sql").read_text()
        return (await conn.fetchrow(sql, account_id, amount))["result"]


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))  # required for Render
    uvicorn.run(app, host="0.0.0.0", port=port)
