"""Kucoin Futures market wrapper class."""

import asyncio
import logging

from kucoin_futures.client import Market

logger = logging.getLogger(__name__)


class KucoinFuturesMarket:
    """Kucoin Futures market wrapper class."""

    def __init__(
        self,
        market: Market = None,
    ):
        """Initialize the Kucoin Futures client."""
        self.market = market

    def get_current_price(self, instrument: str) -> float:
        """Get the current price of an instrument.
        :param instrument: The instrument symbol
        :return: The current price of the instrument"""
        logger.debug("Getting current price for: %s", instrument)
        return float(self.market.get_ticker(instrument)["price"])

    def get_tick_size(self, instrument: str) -> float:  # Unused
        """Get the tick size for an instrument.
        :param instrument: The instrument symbol
        :return: The tick size"""
        logger.debug("Getting tick size for: %s", instrument)
        return self.market.get_contract_detail(instrument)["tickSize"]

    def get_multiplier(self, instrument: str) -> float:  # Unused
        """Get the contract multiplier for an instrument.
        :param instrument: The instrument symbol
        :return: The contract multiplier"""
        logger.debug("Getting multiplier for: %s", instrument)
        return self.market.get_contract_detail(instrument)["multiplier"]

    async def poll_for_entry(
        self,
        instrument: str,
        entry_low: float,
        entry_high: float,
        interval: int = 3,
        max_attempts: int = 2400,
    ) -> None:
        """
        Wait for the current price to be within the entry range.
        :param instrument: The instrument symbol
        :param entry_low: The lower bound of the entry range
        :param entry_high: The upper bound of the entry range
        :param interval: The interval in seconds between each check. Default is 3 seconds.
        :param max_attempts: The maximum number of attempts to make before giving up. Default is 2400.
        :return: None if the entry requirements are met
        :raises TimeoutError: If the entry requirements are not met within the timeout period
        """
        logger.debug("Polling for entry for: %s", instrument)
        attempt = 0
        while attempt < max_attempts:
            current_price = self.get_current_price(instrument)
            logger.debug(
                "Checking entry, current price %s is within %s - %s",
                current_price,
                entry_low,
                entry_high,
            )
            if entry_low <= current_price <= entry_high:
                logger.info("Entry requirements are met.")
                return None
            logger.info(
                "%s price %s is not within entry range %s - %s.",
                instrument,
                current_price,
                entry_low,
                entry_high,
            )
            attempt += 1
            await asyncio.sleep(interval)

        raise TimeoutError("Entry requirements were not met within the timeout period.")
