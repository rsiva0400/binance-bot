from decimal import Decimal
from datetime import datetime, timezone
from uuid import uuid4

from wallet.interface import Wallet
from core.models import Trade


class PaperWallet(Wallet):
    def __init__(
        self,
        starting_balance: Decimal,
        fee_rate: Decimal = Decimal("0.001"),  # 0.1%
        slippage_rate: Decimal = Decimal("0.0002"),  # 0.02%
    ) -> None:
        self._balance = starting_balance
        self._fee_rate = fee_rate
        self._slippage_rate = slippage_rate
        self._open_trade: Trade | None = None

    async def get_balance(self) -> Decimal:
        return self._balance

    async def open_trade(
        self,
        symbol: str,
        price: Decimal,
        quantity: Decimal,
        take_profit: Decimal,
        stop_loss: Decimal,
    ) -> Trade:
        if self._open_trade is not None:
            raise RuntimeError("Trade already open")

        # Simulate slippage on entry (worse price)
        entry_price = price * (Decimal("1") + self._slippage_rate)

        cost = entry_price * quantity
        fee = cost * self._fee_rate
        total_cost = cost + fee

        if total_cost > self._balance:
            raise RuntimeError("Insufficient balance")

        self._balance -= total_cost

        trade = Trade(
            trade_id=str(uuid4()),
            symbol=symbol,
            entry_price=entry_price,
            quantity=quantity,
            take_profit=take_profit,
            stop_loss=stop_loss,
            opened_at=datetime.now(timezone.utc),
        )

        self._open_trade = trade
        return trade

    async def close_trade(
        self,
        trade: Trade,
        exit_price: Decimal,
    ) -> Trade:
        if self._open_trade is None:
            raise RuntimeError("No open trade to close")

        # Simulate slippage on exit (worse price)
        adjusted_exit_price = exit_price * (Decimal("1") - self._slippage_rate)

        gross_value = adjusted_exit_price * trade.quantity
        fee = gross_value * self._fee_rate
        net_value = gross_value - fee

        self._balance += net_value

        pnl = net_value - (trade.entry_price * trade.quantity)

        trade.exit_price = adjusted_exit_price
        trade.closed_at = datetime.now(timezone.utc)
        trade.pnl = pnl

        self._open_trade = None
        return trade
