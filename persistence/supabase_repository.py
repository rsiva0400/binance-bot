from uuid import uuid4
from datetime import datetime, timezone
from decimal import Decimal
import structlog

from core.models import Trade
from persistence.supabase_db import SupabaseDatabase

logger = structlog.get_logger()


class SupabaseTradeRepository:
    """
    Trade repository implementation using Supabase.
    Follows the same interface as TradeRepository but uses Supabase client.
    """

    def __init__(self, db: SupabaseDatabase) -> None:
        """
        Initialize Supabase trade repository.

        Args:
            db: SupabaseDatabase instance
        """
        self._db = db

    async def save_trade(self, trade: Trade) -> None:
        """
        Save a trade to Supabase.

        Args:
            trade: Trade object to save

        Raises:
            Exception: If save operation fails
        """
        client = self._db.get_client()

        try:
            data = {
                "trade_id": str(trade.trade_id),
                "symbol": trade.symbol,
                "entry_price": str(trade.entry_price),
                "exit_price": str(trade.exit_price) if trade.exit_price is not None else None,
                "quantity": str(trade.quantity),
                "pnl": str(trade.pnl) if trade.pnl is not None else None,
                "opened_at": trade.opened_at.isoformat(),
                "closed_at": trade.closed_at.isoformat() if trade.closed_at else None,
            }

            result = client.table("trades").insert(data).execute()

            logger.info(
                "supabase.trade.saved",
                trade_id=trade.trade_id,
                symbol=trade.symbol,
            )

        except Exception as exc:
            logger.error(
                "supabase.trade.save_failed",
                trade_id=trade.trade_id,
                error=str(exc),
            )
            raise

    async def get_trade(self, trade_id: str) -> dict | None:
        """
        Retrieve a trade by ID.

        Args:
            trade_id: Trade ID to retrieve

        Returns:
            Trade data as dictionary or None if not found
        """
        client = self._db.get_client()

        try:
            result = (
                client.table("trades")
                .select("*")
                .eq("trade_id", trade_id)
                .execute()
            )

            if result.data:
                return result.data[0]
            return None

        except Exception as exc:
            logger.error(
                "supabase.trade.get_failed",
                trade_id=trade_id,
                error=str(exc),
            )
            raise

    async def get_recent_trades(self, limit: int = 10) -> list[dict]:
        """
        Get recent trades ordered by opened_at descending.

        Args:
            limit: Maximum number of trades to return

        Returns:
            List of trade dictionaries
        """
        client = self._db.get_client()

        try:
            result = (
                client.table("trades")
                .select("*")
                .order("opened_at", desc=True)
                .limit(limit)
                .execute()
            )

            return result.data

        except Exception as exc:
            logger.error("supabase.trades.get_recent_failed", error=str(exc))
            raise


class SupabaseEventRepository:
    """
    Event repository implementation using Supabase.
    Follows the same interface as EventRepository but uses Supabase client.
    """

    def __init__(self, db: SupabaseDatabase) -> None:
        """
        Initialize Supabase event repository.

        Args:
            db: SupabaseDatabase instance
        """
        self._db = db

    async def log_event(self, event_type: str, message: str) -> None:
        """
        Log an event to Supabase.

        Args:
            event_type: Type of event (e.g., "TRADE_OPEN", "TRADE_CLOSE")
            message: Event message

        Raises:
            Exception: If log operation fails
        """
        client = self._db.get_client()

        try:
            data = {
                "id": str(uuid4()),
                "event_type": event_type,
                "message": message,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            result = client.table("bot_events").insert(data).execute()

            logger.debug(
                "supabase.event.logged",
                event_type=event_type,
                message=message,
            )

        except Exception as exc:
            logger.error(
                "supabase.event.log_failed",
                event_type=event_type,
                error=str(exc),
            )
            # Don't raise - event logging should not break the trading flow
            pass

    async def get_recent_events(self, limit: int = 50) -> list[dict]:
        """
        Get recent events ordered by created_at descending.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of event dictionaries
        """
        client = self._db.get_client()

        try:
            result = (
                client.table("bot_events")
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return result.data

        except Exception as exc:
            logger.error("supabase.events.get_recent_failed", error=str(exc))
            raise
