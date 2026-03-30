WITH wallet AS (
    SELECT id, bal
    FROM mywallet.wallets
    WHERE account_id = $1
),
tx AS (
    UPDATE mywallet.wallets
    SET bal = bal - $2
    WHERE account_id = $1
      AND bal >= $2
    RETURNING id, bal
),
ledger_insert AS (
    INSERT INTO mywallet.wallet_ledger (wallet_id, description, amount, balance_after)
    SELECT id, 'Debit', -$2, bal
    FROM tx
    RETURNING wallet_id
)
SELECT json_build_object(
    'account_id', $1,
    'bal', COALESCE(tx.bal, wallet.bal, 0),
    'status', CASE
        WHEN wallet.id IS NULL THEN 'not_found'
        WHEN tx.id IS NULL THEN 'insufficient_funds'
        ELSE 'success'
    END
) AS result
FROM wallet
LEFT JOIN tx ON tx.id = wallet.id
LIMIT 1;
