WITH inserted AS (
    INSERT INTO mywallet.wallets (account_id, bal)
    VALUES ('ACC-001', 500000000)
    ON CONFLICT (account_id) DO NOTHING
    RETURNING id, account_id, bal
),
existing AS (
    SELECT id, account_id, bal
    FROM mywallet.wallets
    WHERE account_id = 'ACC-001'
),
ledger AS (
    INSERT INTO mywallet.wallet_ledger (wallet_id, description, amount, balance_after)
    SELECT 
        COALESCE(inserted.id, existing.id),
        'Opening Balance',
        500000000,
        500000000
    FROM existing
    LEFT JOIN inserted ON true
    WHERE NOT EXISTS (
        SELECT 1
        FROM mywallet.wallet_ledger
        WHERE wallet_id = existing.id
          AND description = 'Opening Balance'
    )
    RETURNING wallet_id, amount, balance_after
)
SELECT json_build_object(
    'status',
    CASE 
        WHEN EXISTS (SELECT 1 FROM inserted) THEN 'created'
        ELSE 'already_exists'
    END,
    'account_id', 'ACC-001',
    'bal', 500000000,
    'amount', 500000000
) AS result;
