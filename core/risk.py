from datetime import datetime, timedelta, timezone
from decimal import Decimal

from core.enums import BotState


class RiskManager:
    def __init__(
        self,
        max_daily_loss: Decimal,
        max_trades_per_day: int,
        cooldown_minutes: int,
        trading_start_hour: int,
        trading_end_hour: int,
    ) -> None:
        self._max_daily_loss = max_daily_loss
        self._max_trades = max_trades_per_day
        self._cooldown = timedelta(minutes=cooldown_minutes)
        self._start_hour = trading_start_hour
        self._end_hour = trading_end_hour

        self._daily_pnl: Decimal = Decimal("0")
        self._trades_today: int = 0
        self._last_loss_time: datetime | None = None
        self._current_day: datetime.date = datetime.now(timezone.utc).date()

    def reset_if_new_day(self) -> None:
        today = datetime.now(timezone.utc).date()
        if today != self._current_day:
            self._current_day = today
            self._daily_pnl = Decimal("0")
            self._trades_today = 0
            self._last_loss_time = None

    def record_trade_result(self, pnl: Decimal) -> None:
        self._daily_pnl += pnl
        self._trades_today += 1

        if pnl < 0:
            self._last_loss_time = datetime.now(timezone.utc)

    def can_trade(self) -> tuple[bool, str]:
        self.reset_if_new_day()

        now = datetime.now(timezone.utc)

        # Time window check
        if not (self._start_hour <= now.hour < self._end_hour):
            return False, "Outside trading hours"

        # Daily loss cap
        if self._daily_pnl <= -self._max_daily_loss:
            return False, "Max daily loss reached"

        # Max trades
        if self._trades_today >= self._max_trades:
            return False, "Max trades per day reached"

        # Cooldown after loss
        if self._last_loss_time is not None:
            if now - self._last_loss_time < self._cooldown:
                return False, "In cooldown period"

        return True, "OK"

    def should_stop_bot(self) -> bool:
        return self._daily_pnl <= -self._max_daily_loss
