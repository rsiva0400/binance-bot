from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class MarketSnapshot:
    symbol: str
    price: Decimal
    ema_9: Decimal
    ema_21: Decimal
    vwap: Decimal
    volume_ratio: Decimal
    spread_pct: Decimal
    timestamp: datetime


@dataclass
class Trade:
    trade_id: str
    symbol: str
    entry_price: Decimal
    quantity: Decimal
    take_profit: Decimal
    stop_loss: Decimal
    opened_at: datetime
    exit_price: Optional[Decimal] = None
    closed_at: Optional[datetime] = None
    pnl: Optional[Decimal] = None
