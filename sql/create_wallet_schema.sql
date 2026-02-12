CREATE SCHEMA IF NOT EXISTS mywallet;

GRANT ALL ON SCHEMA mywallet TO CURRENT_USER;

CREATE TABLE IF NOT EXISTS mywallet.wallets (
    id SERIAL PRIMARY KEY,
    account_id TEXT UNIQUE NOT NULL,
    bal BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS mywallet.wallet_ledger (
    id SERIAL PRIMARY KEY,
    wallet_id INTEGER NOT NULL REFERENCES mywallet.wallets(id),
    tx_date TIMESTAMP NOT NULL DEFAULT now(),
    description TEXT,
    amount BIGINT NOT NULL,
    balance_after BIGINT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_wallet_ledger_wallet_id
    ON mywallet.wallet_ledger(wallet_id);