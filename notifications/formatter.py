from core.models import Trade


def trade_open_message(trade: Trade) -> str:
    return (
        f"📈 Trade Opened\n"
        f"Symbol: {trade.symbol}\n"
        f"Entry: {trade.entry_price}\n"
        f"TP: {trade.take_profit}\n"
        f"SL: {trade.stop_loss}"
    )


def trade_close_message(trade: Trade) -> str:
    return (
        f"📉 Trade Closed\n"
        f"Symbol: {trade.symbol}\n"
        f"PnL: {trade.pnl}"
    )
