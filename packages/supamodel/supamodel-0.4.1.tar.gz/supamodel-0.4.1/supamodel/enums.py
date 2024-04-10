import enum
from enum import Enum


class AssetClasses(str, enum.Enum):
    """
    Enumeration of asset classes.

    Attributes:
        EQUITY (str): Represents the equity asset class.
        BOND (str): Represents the bond asset class.
        CURRENCY (str): Represents the currency asset class.
        COMMODITY (str): Represents the commodity asset class.
        CRYPTO (str): Represents the cryptocurrency asset class.
        STOCK (str): Represents the stock asset class.
    """

    EQUITY = "EQUITY"
    BOND = "BOND"
    CURRENCY = "CURRENCY"
    COMMODITY = "COMMODITY"
    CRYPTO = "CRYPTO"
    STOCK = "STOCK"


class TimeInt(str, Enum):
    T_1m = "1m"
    T_3m = "3m"
    T_5m = "5m"
    T_15m = "15m"
    T_30m = "30m"
    T_1H = "1H"
    T_2H = "2H"
    T_4H = "4H"
    T_6H = "6H"
    T_8H = "8H"
    T_12H = "12H"
    T_1D = "1D"
    T_3D = "3D"
    T_1W = "1W"
    T_1M = "1M"


class Chain(str, Enum):
    SOLANA = "solana"
    TERRA = "ethereum"
    POLYGON = "polygon"
    AVALANCHE = "avalanche"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"


class RunState(str, Enum):
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PENDING = "PENDING"


class SystemState(str, Enum):
    LIVE = "LIVE"
    BACKTEST = "BACKTEST"
    SIMULATION = "SIMULATION"
    PAPER = "PAPER"
    DEMO = "DEMO"
    DEVELOPMENT = "DEVELOPMENT"


class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELED = "canceled"
    REJECTED = "rejected"


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"
    TAKE_PROFIT = "take_profit"
    TAKE_PROFIT_LIMIT = "take_profit_limit"
    LIMIT_MAKER = "limit_maker"


class TimeIntSQL(str, Enum):
    T_1m = "1 minute"
    T_3m = "3 minutes"
    T_5m = "5 minutes"
    T_15m = "15 minutes"
    T_30m = "30 minutes"
    T_1H = "1 hour"
    T_2H = "2 hours"
    T_4H = "4 hours"
    T_6H = "6 hours"
    T_8H = "8 hours"
    T_12H = "12 hours"
    T_1D = "1 day"
    T_3D = "3 days"
    T_1W = "1 week"
    T_1M = "1 month"
