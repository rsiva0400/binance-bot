CREATE TABLE IF NOT EXISTS trades (
    trade_id UUID PRIMARY KEY,
    symbol TEXT NOT NULL,
    entry_price NUMERIC NOT NULL,
    exit_price NUMERIC,
    quantity NUMERIC NOT NULL,
    pnl NUMERIC,
    opened_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS decisions (
    id UUID PRIMARY KEY,
    symbol TEXT,
    decision TEXT,
    reason TEXT,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS bot_events (
    id UUID PRIMARY KEY,
    event_type TEXT NOT NULL,
    message TEXT,
    created_at TIMESTAMP NOT NULL
);
