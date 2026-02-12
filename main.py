import asyncpg
from fastapi import FastAPI
from pathlib import Path
from pydantic import BaseModel
import uvicorn

DB_URL = "postgresql://endgame:7414@localhost:5432/enddb"
BASE_DIR = Path(__file__).resolve().parent
SQL_DIR = BASE_DIR / "sql"

app = FastAPI(title="Ledger API")

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

class LedgerRequest(BaseModel):
    account_id: str
    amount: int

@app.post("/ledger")
async def post_ledger(data: LedgerRequest):
    async with pool.acquire() as conn:
        sql = (SQL_DIR / "Wallet_debit.sql").read_text()
        row = await conn.fetchrow(sql, data.account_id, data.amount)
        return row["result"]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)