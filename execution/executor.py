from decimal import Decimal
from datetime import datetime, timedelta, timezone

from core.models import Trade
from wallet.interface import Wallet


class TradeExecutor:
    def __init__(
        self,
        wallet: Wallet,
        trade_amount_usdt: Decimal,
        max_trade_duration_minutes: int = 20,
    ) -> None:
        self._wallet = wallet
        self._trade_amount = trade_amount_usdt
        self._max_duration = timedelta(minutes=max_trade_duration_minutes)
        self._active_trade: Trade | None = None

    @property
    def has_active_trade(self) -> bool:
        return self._active_trade is not None

    async def open_trade(
        self,
        symbol: str,
        market_price: Decimal,
        take_profit: Decimal,
        stop_loss: Decimal,
    ) -> Trade:
        if self._active_trade is not None:
            raise RuntimeError("Active trade already exists")

        quantity = self._calculate_quantity(market_price)

        trade = await self._wallet.open_trade(
            symbol=symbol,
            price=market_price,
            quantity=quantity,
            take_profit=take_profit,
            stop_loss=stop_loss,
        )

        self._active_trade = trade
        return trade

    async def should_close_trade(self, current_price: Decimal) -> bool:
        if self._active_trade is None:
            return False

        trade = self._active_trade

        # TP / SL hit
        if current_price >= trade.take_profit:
            return True
        if current_price <= trade.stop_loss:
            return True

        # Time-based exit
        if datetime.now(timezone.utc) - trade.opened_at >= self._max_duration:
            return True

        return False

    async def close_trade(
        self,
        exit_price: Decimal,
    ) -> Trade:
        if self._active_trade is None:
            raise RuntimeError("No active trade to close")

        trade = await self._wallet.close_trade(
            trade=self._active_trade,
            exit_price=exit_price,
        )

        self._active_trade = None
        return trade

    def _calculate_quantity(self, price: Decimal) -> Decimal:
        """
        Quantity = fixed USDT amount / price
        """
        return (self._trade_amount / price).quantize(Decimal("0.000001"))
