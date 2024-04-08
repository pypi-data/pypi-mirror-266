import asyncio
import inspect
import logging
from typing import Callable, Awaitable, Union, Dict
from unittest.mock import AsyncMock

from kucoin_futures_lib.handlers.base import HandlerABC

logger = logging.getLogger(__name__)


class OcoHandler(HandlerABC):
    """Handler that waits for limit order to be filled and then cancels the stop order."""

    def __init__(
        self,
        limit_order_id: str,
        market_order_id: str,
        instrument: str,
        cancel_order: Union[Callable[[str], None], Callable[[str], Awaitable[None]]],
    ):
        self.limit_order_id = limit_order_id
        self.market_order_id = market_order_id
        self.instrument = instrument
        self._canceled = asyncio.Event()
        self._cancel_order = cancel_order
        self._topic = "/contractMarket/tradeOrders"

    def __repr__(self):
        return f"TpSlHandler({self.limit_order_id}, {self.market_order_id}, {self.instrument})"

    @property
    def topic(self) -> str:
        """Return the topic supported by the handler."""
        return f"{self._topic}:{self.instrument}"

    @property
    def private(self) -> bool:
        """Return the privacy status for the topic."""
        return True

    @property
    def done(self) -> asyncio.Event:
        """Return the done status for the handler."""
        return self._canceled

    async def handle(self, msg: Dict):
        """Handle the trade order message from
        :param msg: The trade order message.
        https://www.kucoin.com/docs/websocket/futures-trading/private-channels/trade-orders
        """
        trade_order = msg.get("data", {})
        order_id = trade_order.get("orderId", "")
        message_type = trade_order.get("type", "")

        if order_id == self.limit_order_id and message_type == "filled":
            logger.info("Limit order %s is done.", self.limit_order_id)
            await self.cancel_order(self.market_order_id)
        elif order_id == self.market_order_id and message_type == "filled":
            logger.info("Market order %s is done.", self.market_order_id)
            self._canceled.set()

    async def cancel_order(self, order_id: str) -> None:
        """Cancel the order based on its type (sync or async)."""
        if inspect.isawaitable(self._cancel_order) or isinstance(
            self._cancel_order, AsyncMock  # For testing
        ):
            await self._cancel_order(order_id)
        else:
            self._cancel_order(order_id)
        self._canceled.set()
