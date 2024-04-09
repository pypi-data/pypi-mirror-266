"""Enum values for tardis.dev apis.

The enum classes are designed to be in accordance with the latest [tardis api](https://docs.tardis.dev/api/http).
"""
from __future__ import annotations

from enum import Enum
from typing import Union
from datetime import datetime


class Exchange(Enum):
    """Subset of exchange Symbol supported by tardis.dev.

    > Note: the **Exchange** here is actually equivalent with **Market** somehow.
    > To extend the support for more exchanges, one can add more enum values here, refer to the [official doc](https://api.tardis.dev/v1/exchanges/).
    """
    # ---- Binance ----
    BINANCE_SPOT = "binance"
    """Binance Spot Market, https://api.tardis.dev/v1/exchanges/binance/"""
    BINANCE_UFUTURES = "binance-futures"
    """Binance USDT Based Future, https://api.tardis.dev/v1/exchanges/binance-futures/"""
    BINANCE_CFUTURES = "binance-delivery"
    """Binance Coin Based Future, https://api.tardis.dev/v1/exchanges/binance-delivery/"""
    BINANCE_OPTIONS = "binance-options"
    """Binance Vinilla Options, https://api.tardis.dev/v1/exchanges/binance-options/"""
    BINANCE_EURO_OPTIONS = "binance-european-options"
    """Binance European Options, https://api.tardis.dev/v1/exchanges/binance-european-options/"""

    # ---- OKEX ----
    OKX_SPOT = "okex"
    OKX_SWAP = "okex-swap"
    OKX_FUTURES = "okex-futures"
    OKX_OPTIONS = "okex-options"
    

    @classmethod
    def from_value(cls, value: str) -> Union[Exchange, None]:
        """Reconstruct Exchange enum from exchange value

        Args:
            name (str): the enum value

        Returns:
            Exchange: Exchange enum
        """
        for exchange in cls:
            if exchange.value == value:
                return exchange
        return None


class DataType(Enum):
    """Subset of data types supported by tardis.dev.

    Reference: https://docs.tardis.dev/faq/data
    """
    INCREMENTAL_BOOK_L2 = "incremental_book_L2"
    TRADES = "trades"
    QUOTES = "quotes"
    BOOK_TICKER = "book_ticker"
    BOOK_SNAPSHOT_25 = "book_snapshot_25"
    BOOK_SNAPSHOT_5 = "book_snapshot_5"
    DERIVATIVE_TICKER = "derivative_ticker"
    """Derivative Ticker, Only Available for Future/Option symbols"""
    LIQUIDATIONS = "liquidations"
    """Liquidations, Only Available for Future/Option symbols"""
    KLINE = "kline"
    """Only valid for synthetic kline data. Not a Native Data Type."""

    @classmethod
    def from_value(cls, value: str) -> Union[DataType, None]:
        """Reconstruct DataType enum from data type value

        Args:
            name (str): the enum value

        Returns:
            DataType: DataType enum
        """
        for data_type in cls:
            if data_type.value == value:
                return data_type
        return None

    def to_fileflag(self) -> str:
        """Get file flag for the data type.

        Returns:
            str: file flag
        """
        return DATATYPE_TO_FILEFLAG[self]


DATATYPE_TO_FILEFLAG: dict[DataType, str] = {
    DataType.INCREMENTAL_BOOK_L2: "DELTA",
    DataType.TRADES: "TRADE",
    DataType.QUOTES: "QUOTE",
    DataType.BOOK_TICKER: "BOOKTICKER",
    DataType.BOOK_SNAPSHOT_25: "SNAPSHOT25",
    DataType.BOOK_SNAPSHOT_5: "SNAPSHOT5",
    DataType.DERIVATIVE_TICKER: "DERIVATIVE",
    DataType.LIQUIDATIONS: "LIQUIDATION",
    DataType.KLINE: "KLINE",
}


def get_gzip_file_relpath(exchange: Exchange, data_type: DataType, date: Union[str, datetime], symbol: str) -> str:
    """The relative path of the data file
    
    Example: 
    
    `/home/stevengao/tardis_data/raw/2024/03/22/BINANCE/UFUTURES/BTCUSDT/BINANCE_UFUTURES_BTCUSDT_SNAPSHOT25_2024_03_22.csv.gz`
    """
    exch, market_type = exchange.name.split("_")
    if isinstance(date, str):
        year, month, day = map(int, date.split("-"))
    else:
        year, month, day = date.year, date.month, date.day
    symbol = symbol.upper()

    return f"{year:04d}/{month:02d}/{day:02d}/{exch}/{market_type}/{symbol}/{exch}_{market_type}_{symbol}_{data_type.to_fileflag()}_{year:04d}_{month:02d}_{day:02d}.csv.gz"


__all__ = [
    "DataType",
    "Exchange",
    "get_gzip_file_relpath",
]
