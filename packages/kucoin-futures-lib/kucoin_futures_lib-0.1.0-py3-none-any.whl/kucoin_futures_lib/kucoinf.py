import logging
from typing import Optional, Literal

from kucoin_futures_lib.market import KucoinFuturesMarket
from kucoin_futures_lib.trade import KucoinFuturesTrade
from kucoin_futures_lib.user import KucoinFuturesUser
from kucoin_futures_lib.websocket import KucoinFuturesWebsocket

logger = logging.getLogger(__name__)


class KucoinFutures:
    """Kucoin Futures wrapper class."""

    def __init__(
        self,
        user: KucoinFuturesUser,
        trade: KucoinFuturesTrade,
        market: KucoinFuturesMarket,
        websocket: KucoinFuturesWebsocket,
    ):
        """Initialize the Kucoin Futures client."""
        self.user = user
        self.trade = trade
        self.market = market
        self.websocket = websocket

    @staticmethod
    def _validate_values(value1, value2):
        """Check if two values are both None or not None."""
        if not (value1 is None) == (value2 is None):
            raise ValueError("Both values must be None or not None.")

    async def create_order(
        self,
        instrument: str,
        side: str,
        size: int,
        take_profit: float,
        stop_loss: float,
        price: Optional[float] = None,
        take_profit_type: Literal["limit", "stop"] = "limit",
        stop_loss_type: Literal["limit", "stop"] = "stop",
        leverage: Optional[int] = None,
        enable_oco: bool = True,
    ) -> str:
        """Create order with stop loss and take profit."""
        logger.debug("Creating order: %s %s %s %s", instrument, side, size, price)
        entry_order_id = self.trade.create_order(
            instrument=instrument,
            side=side,
            size=size,
            price=price,
            leverage=leverage,
        )

        await self.websocket.listen_for_fill(order_id=entry_order_id)

        order_ids = self.trade.create_stop_loss_and_take_profit(
            instrument=instrument,
            side=side,
            take_profit=take_profit,
            stop_loss=stop_loss,
            take_profit_type=take_profit_type,
            stop_loss_type=stop_loss_type,
        )

        if enable_oco and take_profit_type == "limit" and stop_loss_type == "stop":
            await self.websocket.tp_sl_cancel(
                tp_order_id=order_ids.tp_order_id,
                sl_order_id=order_ids.sl_order_id,
                instrument=instrument,
                cancel_order=self.trade.cancel_order,
            )

        return entry_order_id
