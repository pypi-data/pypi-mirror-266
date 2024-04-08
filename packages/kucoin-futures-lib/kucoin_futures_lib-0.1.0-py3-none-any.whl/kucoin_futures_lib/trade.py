"""Kucoin Futures trade wrapper class."""

import asyncio
import json
import logging
from collections import namedtuple
from typing import List, Dict, Any, Optional, Literal

from kucoin_futures.client import Trade

logger = logging.getLogger(__name__)


TpSlOrderIds = namedtuple("OrderIds", "tp_order_id sl_order_id")


class KucoinFuturesTrade:
    """Kucoin Futures trade wrapper class."""

    def __init__(
        self,
        trade: Trade = None,
        leverage: int = 2,
    ):
        """Initialize the Kucoin Futures client."""
        self.trade = trade
        self.leverage = leverage

    def get_open_orders(self, instrument: str = None) -> List[Dict[str, Any]]:  # Unused
        """https://www.kucoin.com/docs/rest/futures-trading/orders/get-order-list
        :param instrument: The instrument symbol
        :return: A dictionary containing the open orders for the instrument"""
        logger.debug("Getting open orders")
        response = self.trade.get_order_list()
        if instrument:
            open_orders = [
                order for order in response["items"] if order["symbol"] == instrument
            ]
        else:
            open_orders = response["items"]
        return open_orders

    def cancel_order(self, order_id: str) -> None:
        """Cancel an order by order id.
        https://www.kucoin.com/docs/rest/futures-trading/orders/cancel-order-by-orderid
        """
        logger.debug("Cancelling order by order id: %s", order_id)
        self.trade.cancel_order(orderId=order_id)
        logger.info("Order %s cancel request sent.", order_id)

    async def cancel_order_and_wait(self, order_id: str) -> None:
        """Cancel an order by order id and wait for it to be done."""
        self.cancel_order(order_id)
        await self.poll_for_done(order_id)
        logger.info("Order %s has been cancelled", order_id)

    def create_take_profit_limit(
        self,
        instrument: str,
        entry_side: str,
        tp_price: float,
    ) -> str:
        """Create a take profit order using limit order.
        https://www.kucoin.com/docs/rest/futures-trading/orders/place-order
        """
        response = self.trade.create_limit_order(
            symbol=instrument,
            side="buy" if entry_side == "sell" else "sell",
            price=str(tp_price),
            timeInForce="GTC",
            closeOrder=True,
            lever=None,
            size=None,
        )
        logger.info(
            "Take profit (limit) order created for %s at %s", instrument, tp_price
        )
        return response["orderId"]

    def create_take_profit_stop(
        self,
        instrument: str,
        entry_side: str,
        tp_price: float,
    ) -> str:
        """Create take profit order using stop market order.
        https://www.kucoin.com/docs/rest/futures-trading/orders/place-order
        """
        side, stop = ("sell", "up") if entry_side == "buy" else ("buy", "down")
        response = self.trade.create_market_order(
            symbol=instrument,
            side=side,
            stop=stop,
            stopPriceType="TP",
            stopPrice=str(tp_price),
            timeInForce="GTC",
            closeOrder=True,
            size=None,
            lever=None,
        )
        logger.info(
            "Take profit (stop) order created for %s at %s", instrument, tp_price
        )
        return response["orderId"]

    def create_stop_loss_stop(
        self,
        instrument: str,
        entry_side: str,
        sl_price: float,
    ) -> str:
        """Create stop loss order using stop market order.
        https://www.kucoin.com/docs/rest/futures-trading/orders/place-order
        :param instrument: Instrument symbol
        :param entry_side: Entry order side (buy or sell)
        :param sl_price: Take profit price
        :return: The order id of the stop loss order
        """
        side, stop = ("sell", "down") if entry_side == "buy" else ("buy", "up")
        response = self.trade.create_market_order(
            symbol=instrument,
            side=side,
            stop=stop,
            lever=None,
            stopPriceType="TP",
            stopPrice=str(sl_price),
            timeInForce="GTC",
            closeOrder=True,
        )
        logger.info("Stop loss order (stop) created for %s at %s", instrument, sl_price)
        return response["orderId"]

    def create_stop_loss_limit(
        self,
        instrument: str,
        entry_side: str,
        sl_price: float,
    ) -> str:
        """Create stop loss order using stop limit order.
        https://www.kucoin.com/docs/rest/futures-trading/orders/place-order
        :param instrument: Instrument symbol
        :param entry_side: Entry order side (buy or sell)
        :param sl_price: Take profit price
        :return: The order id of the stop loss order
        """
        side, stop = ("sell", "down") if entry_side == "buy" else ("buy", "up")
        response = self.trade.create_limit_order(
            symbol=instrument,
            side=side,
            stop=stop,
            stopPriceType="TP",
            price=str(sl_price),
            stopPrice=str(sl_price),
            timeInForce="GTC",
            closeOrder=True,
            size=None,
            lever=None,
        )
        logger.info(
            "Stop loss order (limit) created for %s at %s", instrument, sl_price
        )
        return response["orderId"]

    def create_market_order(
        self,
        instrument: str,
        side: str,
        size: int,
        leverage: Optional[int] = None,
    ) -> str:
        """Create a market order with optional stop loss and take profit.
        https://www.kucoin.com/docs/rest/futures-trading/orders/place-order
        :param instrument: The instrument symbol
        :param side: The side of the order (buy or sell)
        :param size: The size of the order in lots
        :param leverage: The leverage to use
        :return: The order id of the entry order
        """
        side = side.lower()
        leverage = leverage or self.leverage
        response = self.trade.create_market_order(
            symbol=instrument, side=side, size=str(size), lever=str(leverage)
        )
        entry_order_id = response["orderId"]
        logger.info(
            "Created market %s order for %s with id %s",
            side,
            instrument,
            entry_order_id,
        )
        return entry_order_id

    def create_limit_order(
        self,
        instrument: str,
        side: str,
        size: int,
        price: float,
        leverage: Optional[int] = None,
    ) -> str:
        """Create a market order with optional stop loss and take profit.
        https://www.kucoin.com/docs/rest/futures-trading/orders/place-order
        :param instrument: The instrument symbol
        :param side: The side of the order (buy or sell)
        :param size: The size of the order in lots
        :param price: The limit price
        :param leverage: The leverage to use
        :return: The order id of the entry order
        """
        side = side.lower()
        leverage = leverage or self.leverage

        response = self.trade.create_limit_order(
            symbol=instrument,
            side=side,
            lever=str(leverage),
            size=str(size),
            price=str(price),
        )
        entry_order_id = response.get("orderId")
        logger.info(
            "Created limit %s order for %s with id %s", side, instrument, entry_order_id
        )
        return entry_order_id

    def create_stop_loss_and_take_profit(
        self,
        instrument: str,
        side: str,
        take_profit: float,
        stop_loss: float,
        take_profit_type: Literal["limit", "stop"] = "limit",
        stop_loss_type: Literal["limit", "stop"] = "stop",
    ) -> TpSlOrderIds:
        """Convenience method to create stop loss and take profit orders for an open position."""

        if take_profit_type == "stop":
            tp_order_id = self.create_take_profit_stop(
                instrument=instrument, entry_side=side, tp_price=take_profit
            )
        else:  # take_profit_type == "limit" if take_profit_type is incorrect default to limit
            tp_order_id = self.create_take_profit_limit(
                instrument=instrument, entry_side=side, tp_price=take_profit
            )

        if stop_loss_type == "limit":
            sl_order_id = self.create_stop_loss_limit(
                instrument=instrument, entry_side=side, sl_price=stop_loss
            )
        else:  # stop_loss_type == "stop" if stop_loss_type is incorrect default to stop
            sl_order_id = self.create_stop_loss_stop(
                instrument=instrument, entry_side=side, sl_price=stop_loss
            )

        return TpSlOrderIds(tp_order_id, sl_order_id)

    def create_order(
        self,
        instrument: str,
        side: str,
        size: int,
        price: Optional[float] = None,
        leverage: Optional[int] = None,
    ) -> str:
        """Convenience method to create either a market or limit order.
        :returns: The order id of the created order.
        """
        if price:  # Order is a limit order
            order_id = self.create_limit_order(
                instrument=instrument,
                side=side,
                size=size,
                price=price,
                leverage=leverage,
            )
        else:
            order_id = self.create_market_order(
                instrument=instrument, side=side, size=size, leverage=leverage
            )
        return order_id

    async def poll_for_fill(
        self, order_id: str, interval: int = 0.3, max_attempts: int = 10
    ) -> Dict[str, Any]:
        """
        Polls the get_recent_fills() endpoint periodically to check if an order has been filled.
        https://www.kucoin.com/docs/rest/futures-trading/fills/get-recent-filled-list
        :param order_id: The ID of the order to wait for a fill.
        :param interval: The interval in seconds between each poll. Default is 5 seconds.
        :param max_attempts: The maximum number of attempts to make before giving up. Default is 720.
        :return: A dictionary containing the fill details of the matching order if found.
        :raises TimeoutError: If `order_id` is not found after the maximum number of attempts.
        """
        attempt = 0
        while attempt < max_attempts:
            recent_fills = self.trade.get_recent_fills()
            logger.debug("Recent fills: %s", json.dumps(recent_fills))
            if isinstance(recent_fills, list):
                for fill in recent_fills:
                    if isinstance(fill, dict) and fill.get("orderId", "") == order_id:
                        logger.info("Order %s has been filled.", order_id)
                        return fill
                logger.info("Order %s has not been filled yet.", order_id)
            else:
                logger.warning("Unexpected recent fills response: %s", recent_fills)
            attempt += 1
            logger.info(
                "Order %s has not been filled yet. Attempt %s/%s",
                order_id,
                attempt,
                max_attempts,
            )
            await asyncio.sleep(interval)

        raise TimeoutError(
            f"Order {order_id} was not filled within the timeout period."
        )

    async def poll_for_done(
        self, order_id: str, interval: int = 1, max_attempts: int = 20
    ) -> Dict[str, Any]:
        """
        Polls the get_order_details() endpoint periodically to check if an order status changes to done.
        https://www.kucoin.com/docs/rest/futures-trading/orders/get-order-details-by-orderid-clientoid
        :param order_id: Order ID to wait for done status.
        :param interval: The interval in seconds between each poll. Default is 1 second.
        :param max_attempts: The maximum number of attempts to make before giving up. Default is 20.
        :return: A dictionary containing the order details if the order status is done.
        """
        attempt = 0
        while attempt < max_attempts:
            order_details = self.trade.get_order_details(order_id)
            logger.info("Order details: %s", json.dumps(order_details))
            if order_details["status"] == "done":
                logger.info("Order %s is done.", order_id)
                return order_details
            attempt += 1
            logger.info(
                "Order %s is not done yet. Attempt %s/%s",
                order_id,
                attempt,
                max_attempts,
            )
            await asyncio.sleep(interval)

        raise TimeoutError(
            f"Order {order_id} was not filled within the timeout period."
        )
