INSERT INTO mywallet.wallets (account_id, bal)
VALUES ('ACC-001', 500000000)
ON CONFLICT (account_id) DO NOTHING;


INSERT INTO mywallet.wallet_ledger (wallet_id, description, amount, balance_after)
SELECT id, 'Opening Balance', bal, bal
FROM mywallet.wallets
WHERE account_id = 'ACC-001'
