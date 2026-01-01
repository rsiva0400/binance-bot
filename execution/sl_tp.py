from decimal import Decimal


def calculate_take_profit(entry_price: Decimal, tp_pct: Decimal) -> Decimal:
    return entry_price * (Decimal("1") + tp_pct)


def calculate_stop_loss(entry_price: Decimal, sl_pct: Decimal) -> Decimal:
    return entry_price * (Decimal("1") - sl_pct)
