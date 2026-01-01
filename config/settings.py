from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    # ---- General ----
    trading_mode: Literal["PAPER", "LIVE"] = "PAPER"
    environment: Literal["DEV", "PROD"] = "DEV"

    # ---- Binance ----
    binance_api_key: str = Field(..., env="BINANCE_API_KEY")
    binance_api_secret: str = Field(..., env="BINANCE_API_SECRET")

    # ---- Trading ----
    symbols: list[str] = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
        "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "MATICUSDT",
        "LTCUSDT", "TRXUSDT", "DOTUSDT", "OPUSDT", "ATOMUSDT",
    ]
    trade_amount_usdt: float = 40.0  # ≈ ₹3–4k
    max_trades_per_day: int = 10

    take_profit_pct: float = 0.009   # 0.9%
    stop_loss_pct: float = 0.0065    # 0.65%

    # ---- Risk ----
    max_daily_loss_usdt: float = 2.0
    cooldown_minutes: int = 60

    # ---- Time Window (24/7 Trading) ----
    trading_start_hour: int = 0
    trading_end_hour: int = 24

    # ---- Database ----
    database_type: Literal["LOCAL", "SUPABASE"] = Field(default="SUPABASE", env="DATABASE_TYPE")
    database_url: str = Field(default="", env="DATABASE_URL")  # For local PostgreSQL
    supabase_url: str = Field(default="", env="SUPABASE_URL")
    supabase_key: str = Field(default="", env="SUPABASE_KEY")

    # ---- Notifications ----
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    class Config:
        env_file = ".env"
        extra = "forbid"


settings = Settings()
