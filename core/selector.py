from core.models import MarketSnapshot


def momentum_score(snapshot: MarketSnapshot) -> float:
    """
    Simple, explainable scoring
    """
    return float(snapshot.volume_ratio + (snapshot.ema_9 - snapshot.ema_21))


def select_best(candidates: list[MarketSnapshot]) -> MarketSnapshot | None:
    if not candidates:
        return None

    return max(candidates, key=momentum_score)
