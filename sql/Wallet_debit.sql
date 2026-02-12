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
)
SELECT json_build_object(
    'account_id', $1,
    'bal', COALESCE(tx.bal, wallet.bal),
    'status', CASE
        WHEN tx.id IS NULL THEN 'insufficient_funds'
        ELSE 'success'
    END
) AS result
FROM wallet
LEFT JOIN tx ON tx.id = wallet.id;