from decimal import Decimal
from core.models import MarketSnapshot


def entry_conditions(snapshot: MarketSnapshot) -> bool:
    """
    Strict momentum + liquidity conditions
    """

    if snapshot.spread_pct >= Decimal("0.08"):
        return False

    if snapshot.ema_9 < snapshot.ema_21 * Decimal("1.0003"):
        return False

    if snapshot.price < snapshot.vwap * Decimal("0.9995"):
        return False

    if snapshot.volume_ratio < Decimal("1.1"):
        return False

    return True
