"""A collection of helper functions for the Kucoin wrapper."""

import logging
import math
from decimal import Decimal

logger = logging.getLogger(__name__)


class KucoinFuturesHelper:
    """Kucoin Helpers mixin class."""

    @staticmethod
    def calculate_lots(
        lot_size: float, current_price: float, investment_amount: float,
    ) -> int:
        """Calculate the maximum number of lots to buy based on the investment amount, current price, and lot size.
        :param lot_size: The lot size for the instrument. E.g. 0.001 for BTC/USDT.
        :param current_price: The current price of the instrument.
        :param investment_amount: The maximum amount to invest.
        :return: The maximum number of lots to buy.
        """
        logger.debug(
            "Calculating lots to buy with investment amount %s, current price %s, and lot size %s",
            investment_amount,
            current_price,
            lot_size,
        )

        if lot_size == 0 or current_price == 0 or investment_amount == 0:
            return 0

        current_price = Decimal(str(current_price))
        investment_amount = Decimal(str(investment_amount))
        lot_size = Decimal(str(lot_size))

        lot_price = current_price * lot_size
        lots = (investment_amount / lot_price).to_integral_value(rounding='ROUND_FLOOR')  # Use Decimal's floor rounding
        return int(lots)

    @staticmethod
    def calculate_precision(tick_size: float) -> int:
        """Calculate the precision of a tick size.
        :param tick_size: The tick size to calculate the precision of.
        :return: The precision of the tick size.
        """
        logger.debug("Calculating precision of tick size %s", tick_size)
        return int(-math.log10(tick_size))
