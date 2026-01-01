from abc import ABC, abstractmethod
from decimal import Decimal
from core.models import Trade


class Wallet(ABC):
    @abstractmethod
    async def get_balance(self) -> Decimal:
        ...

    @abstractmethod
    async def open_trade(
        self,
        symbol: str,
        price: Decimal,
        quantity: Decimal,
        take_profit: Decimal,
        stop_loss: Decimal,
    ) -> Trade:
        ...

    @abstractmethod
    async def close_trade(
        self,
        trade: Trade,
        exit_price: Decimal,
    ) -> Trade:
        ...
