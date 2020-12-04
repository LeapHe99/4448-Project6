
from enum import Enum


class Direction(Enum):

    LONG = "LONG"
    SHORT = "SHORT"




class OrderType(Enum):
    """
    Order type.
    """
    LIMIT = "LIMIT"
    # MARKET = "MARET"


class Exchange(Enum):
    """
    Exchange.
    """

    # Global
    SMART = "SMART"         # Smart Router for US stocks
    NYMEX = "NYMEX"         # New York Mercantile Exchange

