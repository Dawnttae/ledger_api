import os
import uvicorn
import asyncpg
from fastapi import FastAPI
from pathlib import Path
from pydantic import BaseModel

DB_URL = os.environ.get("DATABASE_URL")  # ✅ use Render env var
BASE_DIR = Path(__file__).resolve().parent
SQL_DIR = BASE_DIR / "sql"

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
        await run_sql_file(conn, "create_wallet_schema.sql")
        await run_sql_file(conn, "Seed_wallet.sql")



@app.on_event("shutdown")
async def shutdown():
    if pool:
        await pool.close()


@app.get("/")  # ✅ IMPORTANT health check route
async def root():
    return {"status": "ok"}

class LedgerRequest(BaseModel):
    account_id: str
    amount: int
    bal: int

@app.post("/ledger")
async def post_ledger(data: LedgerRequest):
    async with pool.acquire() as conn:
        seed_sql = (SQL_DIR / "Seed_wallet.sql").read_text()
        await conn.execute(seed_sql)
        debit_sql = (SQL_DIR / "Wallet_debit.sql").read_text()
        row = await conn.fetchrow(debit_sql, data.account_id, data.amount,data.bal)
        return row["result"]



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))  # required for Render
    uvicorn.run(app, host="0.0.0.0", port=port)
