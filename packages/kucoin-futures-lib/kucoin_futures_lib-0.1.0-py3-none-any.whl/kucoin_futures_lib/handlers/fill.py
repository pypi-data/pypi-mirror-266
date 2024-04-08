import asyncio
import logging
from typing import Dict

from kucoin_futures_lib.handlers.base import HandlerABC

logger = logging.getLogger(__name__)


class FillHandler(HandlerABC):

    def __init__(
        self,
        order_id: str,
    ):
        self.order_id = order_id
        self._filled = asyncio.Event()
        self._topic = "/contractMarket/tradeOrders"

    def __repr__(self):
        return f"FillHandler('{self.order_id}')"

    @property
    def topic(self) -> str:
        """Return the topic supported by the handler."""
        return f"{self._topic}"

    @property
    def private(self) -> bool:
        """Return the privacy status for the topic."""
        return True

    @property
    def done(self) -> asyncio.Event:
        """Return the done status for the handler."""
        return self._filled

    async def handle(self, msg: Dict):
        """Handle the trade order message from
        :param msg: The trade order message.
        https://www.kucoin.com/docs/websocket/futures-trading/private-channels/trade-orders
        """
        trade_order = msg.get("data", {})
        trade_order_id = trade_order.get("orderId", "")
        message_type = trade_order.get("type", "")

        if trade_order_id == self.order_id and message_type == "filled":
            logger.info("Order %s filled", self.order_id)
            self._filled.set()
