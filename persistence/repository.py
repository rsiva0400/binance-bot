from uuid import uuid4
from datetime import datetime, timezone
from core.models import Trade
from persistence.db import Database


class TradeRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def save_trade(self, trade: Trade) -> None:
        conn = await self._db.acquire()
        try:
            await conn.execute(
                """
                INSERT INTO trades (
                    trade_id, symbol, entry_price, exit_price,
                    quantity, pnl, opened_at, closed_at
                ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
                """,
                trade.trade_id,
                trade.symbol,
                trade.entry_price,
                trade.exit_price,
                trade.quantity,
                trade.pnl,
                trade.opened_at,
                trade.closed_at,
            )
        finally:
            await self._db._pool.release(conn)


class EventRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def log_event(self, event_type: str, message: str) -> None:
        conn = await self._db.acquire()
        try:
            await conn.execute(
                """
                INSERT INTO bot_events (id, event_type, message, created_at)
                VALUES ($1,$2,$3,$4)
                """,
                uuid4(),
                event_type,
                message,
                datetime.now(timezone.utc),
            )
        finally:
            await self._db._pool.release(conn)
