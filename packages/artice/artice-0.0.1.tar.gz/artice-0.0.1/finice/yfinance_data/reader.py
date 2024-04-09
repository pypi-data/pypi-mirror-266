import pytz
import pathlib
import datetime
from typing import Optional, Union

import pandas as pd

from utils import WithLogger
from finice.utils import KlineInterval
from .db.mongodb import FiniceMongoDBClient

tz = pytz.timezone("America/New_York")
"""timezone used to download data from Yahoo Finance"""


class YFPriceLocalReader:
    """Helper class to facilitate reading data from local csv files downloaded by `YFinanceDownloader`
    
    Example Usage:
    ```python
    reader = YFinanceReader()
    # get daily kline from 2021-01-01 to 2021-12-31
    df_daily = reader.read("AAPL", from_date="2021-01-01", to_date="2021-12-31")  
    # get weekly kline since 2020-01-01 to now
    df_weekly = reader.read("TSLA", from_date="2020-01-01", interval="1w") 
    ```
    """
    def __init__(self):
        pass
    
    def read(self, ticker: str, from_date: Optional[str] = None, to_date: Optional[str] = None, interval: str = '1d') -> pd.DataFrame:
        """Read data from local csv files with automatic kline interval detection and data transformation
        
        Args:
            ticker: the ticker symbol
            from_date: the start date(inclusive), If None, read from the oldest available date
            to_date: the end date(inclusive), If None, read till the latest available date
            interval: the time interval, only '1d' is available now
            
        Returns:
            pd.DataFrame: the query result
        """
        interval = KlineInterval.parse(interval)
        if interval < KlineInterval.DAY:
            return self._read_intra_data(ticker, from_date, to_date, interval)
        else:
            return self._read_inter_data(ticker, from_date, to_date, interval)
           
    # TODO: support intraday data reading 
    def _read_intra_data(self, ticker: str, from_date: Optional[str] = None, to_date: Optional[str] = None, interval: KlineInterval = KlineInterval.MINUTE) -> pd.DataFrame:
        """Read from minute-level data, it should locate at ${YFINANCE_PRICE_DATA_DIR}/{ticker}/intra_day/**"""
        raise NotImplementedError("Read intra-day data is not implemented yet.")
            
    def _read_inter_data(self, ticker: str, from_date: Optional[str] = None, to_date: Optional[str] = None, interval: KlineInterval = KlineInterval.DAY) -> pd.DataFrame:
        """Read from daily data, it should locate at ${YFINANCE_PRICE_DATA_DIR}/{ticker}/ "interday"/f"{ticker}_interday_1d.csv"""
        data_dir = self._load_data_dir_from_env()
        csv_path = data_dir / ticker / "interday" / f"{ticker}_interday_1d.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Daily kline data not found for {ticker}")
        df = pd.read_csv(csv_path)
        df['Date'] = df['Date'].apply(lambda x: datetime.datetime.strptime(x.split()[0], "%Y-%m-%d"))
        if from_date:
            df = df[df['Date'] >= from_date]
        if to_date:
            df = df[df['Date'] <= to_date]
        df.reset_index(drop=True, inplace=True)
        return df
    
    def _load_data_dir_from_env(self) -> pathlib.Path:
        from finice.yfinance_data.config import finice_yfinance_config
        if not finice_yfinance_config.data_dir:
            raise ValueError(f"YFINANCE_PRICE_DATA_DIR is not set, please set it in your environment variables or in the .env file, or just pass it to the constructor.")
        return finice_yfinance_config.data_dir


class YFPriceMongoReader(WithLogger):
    def __init__(self):
        super().__init__()
        self.client = FiniceMongoDBClient()

    def read(self, ticker: str, from_date: Optional[str] = None, to_date: Optional[str] = None, as_df: bool = True) -> Optional[Union[list[dict], pd.DataFrame]]:
        """Read articles from MongoDB
        
        Args:
            ticker: (str) ticker symbol
            from_date: (str) date string with format '%Y-%m-%d'
            to_date: (str) date string with format '%Y-%m-%d'

        Returns:
            Union[list[dict], pd.DataFrame]: list of articles
        """
        with self.client:
            klines = self.client.query(ticker=ticker, from_date=from_date, to_date=to_date)
        if as_df:
            df = pd.DataFrame(klines)
            if len(df) == 0:
                # self.logger.warning(f"No kline found for {ticker} in the date range {from_date} to {to_date}.")
                return None
            return df
        else:
            return klines if len(klines) > 0 else None

    def read_around_date(self, ticker:str, target_date: str, history_winsize: int = 45, future_winsize: int = 15) -> pd.DataFrame:
        """
        Args:
            ticker: (str) the ticker symbol
            target_date: (str) the target date to construct the time series
            history_winsize: (int) how many days before the target date should be included
            future_winsize: (int) how many days after the target date should be included
        
        Returns:
            pd.DataFrame: the time series data
            
        Raises:
            ValueError: if the data is not enough to construct the time series
        """
        one_day_after_target_date = datetime.datetime.strptime(target_date, "%Y-%m-%d") + datetime.timedelta(days=1)
        history_df = self.read(ticker=ticker, to_date=target_date, as_df=True)
        if history_df is not None and len(history_df) > history_winsize:
            history_df = history_df.iloc[-history_winsize:]
        else:
            # self.logger.error(f"ticker={ticker}, target_date={target_date} has no history data to construct the time series.")
            raise ValueError(f"ticker={ticker}, target_date={target_date} has no history data to construct the time series.")
        future_df = self.read(ticker=ticker, from_date=one_day_after_target_date.strftime("%Y-%m-%d"), as_df=True)
        if future_df is not None and len(future_df) > future_winsize:
            future_df = future_df.iloc[:future_winsize]
        else:
            # self.logger.error(f"ticker={ticker}, target_date={target_date} has no future data to construct the time series.")
            raise ValueError(f"ticker={ticker}, target_date={target_date} has no future data to construct the time series.")
        
        df = pd.concat([history_df, future_df], axis=0).reset_index(drop=True)
        if len(df) < history_winsize + future_winsize:
            # self.logger.error(f"ticker={ticker}, target_date={target_date} has not enough data to construct the time series, only {len(df)} records found.")
            raise ValueError(f"ticker={ticker}, target_date={target_date} has not enough data to construct the time series, only {len(df)} records found.")
        return df


__all__ = [
    'YFPriceLocalReader',
    'YFPriceMongoReader',
]
