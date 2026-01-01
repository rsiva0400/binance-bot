from decimal import Decimal
from datetime import datetime, timezone

from core.models import MarketSnapshot
from market.indicators import ema, vwap


def build_snapshot(
    symbol: str,
    klines: list[list],
    ticker: dict,
) -> MarketSnapshot:
    closes = [Decimal(k[4]) for k in klines]
    volumes = [Decimal(k[5]) for k in klines]

    ema_9 = ema(closes[-9:], 9)
    ema_21 = ema(closes, 21)
    vwap_value = vwap(closes, volumes)

    best_bid = Decimal(ticker["bidPrice"])
    best_ask = Decimal(ticker["askPrice"])
    spread_pct = ((best_ask - best_bid) / best_bid) * Decimal("100")

    recent_volume = volumes[-1]
    avg_volume = sum(volumes[:-1]) / Decimal(len(volumes) - 1)
    volume_ratio = recent_volume / avg_volume if avg_volume > 0 else Decimal("0")

    return MarketSnapshot(
        symbol=symbol,
        price=closes[-1],
        ema_9=ema_9,
        ema_21=ema_21,
        vwap=vwap_value,
        volume_ratio=volume_ratio,
        spread_pct=spread_pct,
        timestamp=datetime.now(timezone.utc),
    )
