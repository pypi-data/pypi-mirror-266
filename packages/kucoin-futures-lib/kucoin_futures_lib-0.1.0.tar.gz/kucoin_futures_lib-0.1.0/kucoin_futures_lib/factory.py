import logging

from kucoin_futures.client import WsToken, User, Trade, Market

from kucoin_futures_lib.kucoinf import KucoinFutures
from kucoin_futures_lib.market import KucoinFuturesMarket
from kucoin_futures_lib.trade import KucoinFuturesTrade
from kucoin_futures_lib.user import KucoinFuturesUser
from kucoin_futures_lib.websocket import KucoinFuturesWebsocket

logger = logging.getLogger(__name__)


def initialize_kucoinf(
    api_key: str, api_secret: str, api_passphrase: str
) -> KucoinFutures:
    """Initialize the Kucoin Futures client using API credentials."""
    user = initialize_user(api_key, api_secret, api_passphrase)
    trade = initialize_trade(api_key, api_secret, api_passphrase)
    market = initialize_market(api_key, api_secret, api_passphrase)
    websocket = initialize_websocket(api_key, api_secret, api_passphrase)
    kucoinf = KucoinFutures(user=user, trade=trade, market=market, websocket=websocket)
    logger.info("Kucoin Futures client initialized.")
    return kucoinf


def initialize_user(
    api_key: str, api_secret: str, api_passphrase: str
) -> "KucoinFuturesUser":
    """Initialize the Kucoin Futures User client using API credentials."""
    user = User(key=api_key, secret=api_secret, passphrase=api_passphrase)
    return KucoinFuturesUser(user=user)


def initialize_market(
    api_key: str, api_secret: str, api_passphrase: str
) -> KucoinFuturesMarket:
    """Initialize the Kucoin Futures Market client using API credentials."""
    market = Market(key=api_key, secret=api_secret, passphrase=api_passphrase)
    return KucoinFuturesMarket(market=market)


def initialize_trade(
    api_key: str, api_secret: str, api_passphrase: str
) -> KucoinFuturesTrade:
    """Initialize the Kucoin Futures Trade client using API credentials."""
    trade = Trade(key=api_key, secret=api_secret, passphrase=api_passphrase)
    return KucoinFuturesTrade(trade=trade)


def initialize_websocket(
    api_key: str,
    api_secret: str,
    api_passphrase: str,
    url="https://api-futures.kucoin.com",
) -> KucoinFuturesWebsocket:
    """Initialize the Kucoin Futures Websocket client using API credentials."""
    token = WsToken(
        key=api_key,
        secret=api_secret,
        passphrase=api_passphrase,
        url=url,
    )
    return KucoinFuturesWebsocket(token=token)
