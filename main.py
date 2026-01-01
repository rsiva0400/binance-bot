import asyncio
from decimal import Decimal
from config.settings import settings
from utils.logger import setup_logging
from wallet.paper_wallet import PaperWallet
from execution.executor import TradeExecutor
from core.risk import RiskManager
from core.engine import TradingEngine
from persistence.db import Database
from persistence.repository import TradeRepository, EventRepository
from persistence.supabase_db import SupabaseDatabase
from persistence.supabase_repository import SupabaseTradeRepository, SupabaseEventRepository
from notifications.telegram import TelegramNotifier
import structlog

logger = structlog.get_logger()


async def main() -> None:
    wallet = PaperWallet(
        starting_balance=Decimal("100"),
    )

    executor = TradeExecutor(
        wallet=wallet,
        trade_amount_usdt=Decimal(str(settings.trade_amount_usdt)),
    )

    risk = RiskManager(
        max_daily_loss=Decimal(str(settings.max_daily_loss_usdt)),
        max_trades_per_day=settings.max_trades_per_day,
        cooldown_minutes=settings.cooldown_minutes,
        trading_start_hour=settings.trading_start_hour,
        trading_end_hour=settings.trading_end_hour,
    )

    # Initialize database based on configuration
    if settings.database_type == "SUPABASE":
        logger.info("database.using_supabase")
        db = SupabaseDatabase(
            url=settings.supabase_url,
            key=settings.supabase_key,
        )
        await db.connect()
        trade_repo = SupabaseTradeRepository(db)
        event_repo = SupabaseEventRepository(db)
    else:
        logger.info("database.using_local")
        db = Database(settings.database_url)
        await db.connect()
        trade_repo = TradeRepository(db)
        event_repo = EventRepository(db)

    notifier = None
    if settings.telegram_bot_token:
        notifier = TelegramNotifier(
            settings.telegram_bot_token,
            settings.telegram_chat_id,
        )

    engine = TradingEngine(
        symbols=settings.symbols,
        executor=executor,
        risk_manager=risk,
        take_profit_pct=Decimal(str(settings.take_profit_pct)),
        stop_loss_pct=Decimal(str(settings.stop_loss_pct)),
        trade_repo=trade_repo,
        event_repo=event_repo,
        notifier=notifier,
    )

    await engine.run()


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
