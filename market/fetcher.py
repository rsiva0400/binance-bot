import aiohttp
import asyncio
from typing import Any


BINANCE_BASE_URL = "https://api.binance.com"


class BinanceFetcher:
    def __init__(self, timeout_seconds: int = 5) -> None:
        self._timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "BinanceFetcher":
        self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._session:
            await self._session.close()

    async def _get(self, path: str, params: dict[str, Any]) -> Any:
        assert self._session is not None

        async with self._session.get(
            f"{BINANCE_BASE_URL}{path}",
            params=params,
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def fetch_klines(
        self, symbol: str, interval: str = "1m", limit: int = 21
    ) -> list[list[Any]]:
        return await self._get(
            "/api/v3/klines",
            {"symbol": symbol, "interval": interval, "limit": limit},
        )

    async def fetch_ticker(self, symbol: str) -> dict[str, Any]:
        return await self._get("/api/v3/ticker/bookTicker", {"symbol": symbol})
