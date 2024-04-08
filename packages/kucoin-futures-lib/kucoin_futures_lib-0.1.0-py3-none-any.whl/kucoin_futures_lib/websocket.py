"""Kucoin Futures WebSocket module."""

import asyncio
import logging
from typing import Union, Callable, Awaitable, Optional

from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient

from kucoin_futures_lib.handlers import OcoHandler, EntryRangeHandler, HandlerABC, FillHandler

logger = logging.getLogger(__name__)


class KucoinFuturesWebsocket:
    """Kucoin Futures user wrapper class."""

    def __init__(self, token: WsToken):
        self.token = token

    async def subscribe(
        self, handler: HandlerABC, timeout: Optional[float] = 60 * 60 * 12
    ) -> None:
        """Subscribe to the WebSocket topic."""
        ws_client = await KucoinFuturesWsClient.create(
            loop=None,
            client=self.token,
            callback=handler.handle,
            private=handler.private,
        )
        await ws_client.subscribe(handler.topic)
        logger.info("%s subscribed to %s", handler, handler.topic)
        try:
            if timeout:
                await asyncio.wait_for(handler.done.wait(), timeout)
            else:
                await handler.done.wait()
        except asyncio.TimeoutError:
            logger.warning("Timeout reached. Unsubscribing from %s", handler.topic)
            handler.done.set()
        finally:
            await ws_client.unsubscribe(handler.topic)

    async def tp_sl_cancel(
        self,
        tp_order_id: str,
        sl_order_id: str,
        instrument: str,
        cancel_order: Union[Callable[[str], None], Callable[[str], Awaitable[None]]],
    ) -> None:
        """Listen for take profit and stop loss orders and cancel the other order when one is done.
        :param tp_order_id: Take profit order ID
        :param sl_order_id: Stop loss order ID
        :param instrument: Instrument symbol
        :param cancel_order: Function to cancel the order
        """
        handler = OcoHandler(
            limit_order_id=tp_order_id,
            market_order_id=sl_order_id,
            instrument=instrument,
            cancel_order=cancel_order,
        )
        await self.subscribe(handler, None)

    async def listen_for_entry(
        self,
        instrument: str,
        entry_high: float,
        entry_low: float,
        timeout: float = 60 * 60 * 12,
    ) -> None:
        """Listen for the entry price range.
        :param instrument: Instrument symbol
        :param entry_high: Entry high price
        :param entry_low: Entry low price
        :param timeout: timeout in seconds. Default is 12 hours
        """
        handler = EntryRangeHandler(
            instrument=instrument, entry_high=entry_high, entry_low=entry_low
        )
        await self.subscribe(handler, timeout)

    async def listen_for_fill(
        self,
        order_id: str,
        timeout: float = 60 * 60 * 12,
    ) -> None:
        """Listen for the order to be filled.
        :param order_id: Order ID
        :param timeout: timeout in seconds. Default is 12 hours
        """
        handler = FillHandler(order_id=order_id)
        await self.subscribe(handler, timeout)
