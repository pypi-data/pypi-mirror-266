import asyncio
import logging

from kucoin_futures_lib.handlers.base import HandlerABC

logger = logging.getLogger(__name__)


class EntryRangeHandler(HandlerABC):
    """Handler that waits for the instrument to reach a certain price range"""

    def __init__(
        self,
        instrument: str,
        entry_high: float,
        entry_low: float,
    ):
        assert entry_high > entry_low, "Entry high must be greater than entry low"
        self.instrument = instrument
        self.entry_low = entry_low
        self.entry_high = entry_high
        self._entered = asyncio.Event()
        self._topic = "/contractMarket/tickerV2"

    def __repr__(self):
        return f"EntryRangeHandler('{self.instrument}', {self.entry_high}, {self.entry_low})"

    @property
    def done(self) -> asyncio.Event:
        """Return the done status for the handler."""
        return self._entered

    @property
    def topic(self) -> str:
        """Return the topic supported by the handler."""
        return f"{self._topic}:{self.instrument}"

    @property
    def private(self) -> bool:
        """Return the privacy status for the topic."""
        return False

    async def handle(self, msg):
        """Handle the trade order message from
        :param msg: The trade order message.
        https://www.kucoin.com/docs/websocket/futures-trading/public-channels/get-ticker-v2
        """
        ticker = msg.get("data", {})
        best_bid_price = float(ticker.get("bestBidPrice", 0))
        best_ask_price = float(ticker.get("bestAskPrice", 0))
        if best_bid_price >= self.entry_low and best_ask_price <= self.entry_high:
            logger.info(
                "Instrument %s has reached the entry range: %s <= %s <= %s",
                self.instrument,
                self.entry_low,
                best_bid_price,
                self.entry_high,
            )
            self._entered.set()
