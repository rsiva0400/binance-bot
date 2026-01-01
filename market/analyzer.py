import asyncio
from typing import Iterable

from market.fetcher import BinanceFetcher
from market.snapshot import build_snapshot
from core.models import MarketSnapshot


async def analyze_symbol(
    fetcher: BinanceFetcher,
    symbol: str,
) -> MarketSnapshot | None:
    try:
        klines, ticker = await asyncio.gather(
            fetcher.fetch_klines(symbol),
            fetcher.fetch_ticker(symbol),
        )
        return build_snapshot(symbol, klines, ticker)
    except Exception:
        return None


async def analyze_symbols(
    symbols: Iterable[str],
) -> list[MarketSnapshot]:
    async with BinanceFetcher() as fetcher:
        tasks = [analyze_symbol(fetcher, s) for s in symbols]
        results = await asyncio.gather(*tasks)

    return [r for r in results if r is not None]
