from decimal import Decimal
from typing import Iterable


def ema(values: Iterable[Decimal], period: int) -> Decimal:
    values = list(values)
    multiplier = Decimal("2") / (Decimal(period) + Decimal("1"))

    ema_value = values[0]
    for price in values[1:]:
        ema_value = (price - ema_value) * multiplier + ema_value

    return ema_value


def vwap(prices: list[Decimal], volumes: list[Decimal]) -> Decimal:
    total_volume = sum(volumes)
    if total_volume == 0:
        return prices[-1]

    return sum(p * v for p, v in zip(prices, volumes)) / total_volume
