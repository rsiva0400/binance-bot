import asyncio
from decimal import Decimal
import structlog

from core.state_machine import StateMachine
from core.enums import BotState
from core.rules import entry_conditions
from core.selector import select_best
from core.risk import RiskManager
from execution.executor import TradeExecutor
from execution.sl_tp import calculate_take_profit, calculate_stop_loss
from market.analyzer import analyze_symbols
from core.models import MarketSnapshot

logger = structlog.get_logger()


class TradingEngine:
    def __init__(
        self,
        symbols: list[str],
        executor: TradeExecutor,
        risk_manager: RiskManager,
        take_profit_pct: Decimal,
        stop_loss_pct: Decimal,
        poll_interval_seconds: int = 2,
        trade_repo=None,
        event_repo=None,
        notifier=None,
    ) -> None:
        self._symbols = symbols
        self._executor = executor
        self._risk = risk_manager
        self._tp_pct = take_profit_pct
        self._sl_pct = stop_loss_pct
        self._poll_interval = poll_interval_seconds
        self._trade_repo = trade_repo
        self._event_repo = event_repo
        self._notifier = notifier

        self._state_machine = StateMachine()

    async def run(self) -> None:
        logger.info("engine.started")
        self._state_machine.transition(BotState.SCANNING)

        while True:
            try:
                await self._tick()
            except Exception as exc:
                logger.exception("engine.error", error=str(exc))
                await asyncio.sleep(5)

    async def _tick(self) -> None:
        logger.info("engine.tick")
        # 1️⃣ If trade active → monitor exit
        if self._executor.has_active_trade:
            await self._handle_active_trade()
            await asyncio.sleep(1)
            return

        # 2️⃣ Check risk
        allowed, reason = self._risk.can_trade()

        if not allowed:
            logger.info("trade.blocked", reason=reason)
            await asyncio.sleep(self._poll_interval)
            return

        # 3️⃣ Fetch market snapshots
        snapshots = await analyze_symbols(self._symbols)

        # 4️⃣ Apply entry rules
        candidates: list[MarketSnapshot] = [
            s for s in snapshots if entry_conditions(s)
        ]

        # 5️⃣ Select best candidate
        selected = select_best(candidates)

        logger.info("market.selected", selected=selected)
        if not selected:
            await asyncio.sleep(self._poll_interval)
            return

        # 6️⃣ Execute trade
        await self._open_trade(selected)

    async def _open_trade(self, snapshot: MarketSnapshot) -> None:
        logger.info(
            "trade.opening",
            symbol=snapshot.symbol,
            price=str(snapshot.price),
        )

        tp = calculate_take_profit(snapshot.price, self._tp_pct)
        sl = calculate_stop_loss(snapshot.price, self._sl_pct)

        trade = await self._executor.open_trade(
            symbol=snapshot.symbol,
            market_price=snapshot.price,
            take_profit=tp,
            stop_loss=sl,
        )

        self._state_machine.transition(BotState.IN_TRADE)

        logger.info(
            "trade.opened",
            trade_id=trade.trade_id,
            symbol=trade.symbol,
            entry=str(trade.entry_price),
            tp=str(trade.take_profit),
            sl=str(trade.stop_loss),
        )

        # ---- Persistence & Notifications (non-blocking) ----
        try:
            if self._event_repo:
                await self._event_repo.log_event(
                    event_type="TRADE_OPEN",
                    message=f"{trade.symbol} @ {trade.entry_price}",
                )

            if self._notifier:
                from notifications.formatter import trade_open_message
                await self._notifier.send(trade_open_message(trade))

        except Exception as exc:
            logger.warning("trade.open.side_effect_failed", error=str(exc))

    async def _handle_active_trade(self) -> None:
        trade = self._executor._active_trade
        assert trade is not None

        # Fetch only price for the active symbol
        snapshots = await analyze_symbols([trade.symbol])
        if not snapshots:
            return

        current_price = snapshots[0].price

        if not await self._executor.should_close_trade(current_price):
            return

        closed_trade = await self._executor.close_trade(current_price)

        self._risk.record_trade_result(closed_trade.pnl or Decimal("0"))

        logger.info(
            "trade.closed",
            trade_id=closed_trade.trade_id,
            symbol=closed_trade.symbol,
            pnl=str(closed_trade.pnl),
        )
        # ---- Persistence & Notifications (non-blocking) ----
        try:
            if self._trade_repo:
                await self._trade_repo.save_trade(closed_trade)

            if self._event_repo:
                await self._event_repo.log_event(
                    event_type="TRADE_CLOSE",
                    message=f"{closed_trade.symbol} pnl={closed_trade.pnl}",
                )

            if self._notifier:
                from notifications.formatter import trade_close_message
                await self._notifier.send(trade_close_message(closed_trade))

        except Exception as exc:
            logger.warning("trade.close.side_effect_failed", error=str(exc))

        self._state_machine.transition(BotState.COOLDOWN)
        await asyncio.sleep(2)
        self._state_machine.transition(BotState.SCANNING)


