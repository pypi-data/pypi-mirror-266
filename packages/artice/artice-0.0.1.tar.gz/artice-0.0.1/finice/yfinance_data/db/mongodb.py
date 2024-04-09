from __future__ import annotations

import os
import pathlib
import datetime
import traceback
from typing import Optional

import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from pymongo.collection import Collection
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, BulkWriteError

from utils import MongoDBConnector, WithLogger, today_str


class FiniceMongoDBClient(WithLogger):
    def __init__(self, connection_string: Optional[str] = None):
        super().__init__()
        if not connection_string:
            connection_string = self._load_kline_mongodb_connection_string()
        if not connection_string:
            raise ValueError(f"To enable `FiniceMongoDBClient`, you must specify `FINICE_MONGODB_CONNECTION_STRING` in `.env` file or system settings")
        self._connector = MongoDBConnector(connection_string=connection_string)
        self._db_name: str = "finice"
        self._collection_name: str = "yfinance_daily_kline"
        self._collection: Optional[Collection] = None

    @property
    def is_connected(self) -> bool:
        return self._connector.is_connected

    def ensure_index(self) -> None:
        if not self.is_connected:
            raise RuntimeError(f"Please connect first or use the with statement to control context.")
        
        self._collection.create_index([('Date', ASCENDING)], name='date_index')
        self._collection.create_index([('ticker', ASCENDING)], name='ticker_index')
        self._collection.create_index([('ticker', ASCENDING), ('Date', ASCENDING)], name='ticker_date_index', unique=True)

    def insert(self, kline: dict, duplicated_ok: bool = True):
        """Insert one kline to MongoDB database

        Args:
            kline: (dict) the kline data dict
            duplicated_ok: (bool) ignore duplicated key error. Default to True
        """
        if not self.is_connected:
            raise RuntimeError("Please connect first or use with statement")
        try:
            result = self._collection.insert_one(kline)
            return result
        except DuplicateKeyError as e:
            if not duplicated_ok:
                raise e
        
    def insert_many(self, klines: list[dict], duplicated_ok: bool = True, max_batch_size: int = 128):
        if not self.is_connected:
            raise RuntimeError("Please connect first or use with statement")

        for batch_start in range(0, len(klines), max_batch_size):
            try:
                kline_batch = klines[batch_start:batch_start + max_batch_size]
                self._collection.insert_many(kline_batch)
            except DuplicateKeyError as e:
                if not duplicated_ok:
                    raise e
                continue
            except BulkWriteError as e:
                if not duplicated_ok:
                    raise e
                continue

    def query(self, ticker: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> list[dict]:
        """
        Args:
            ticker: (str) ticker symbol
            from_date: (str) date string with format '%Y-%m-%d'
            to_date: (str) date string with format '%Y-%m-%d'
            
        Returns:
            list[dict]: list of klines
        """
        if not self.is_connected:
            raise RuntimeError("Please connect first or use with statement")
        if from_date is None:
            from_date = '1930-01-01'
        if to_date is None:
            to_date = today_str()
        from_date = datetime.datetime.strptime(from_date, '%Y-%m-%d')
        to_date = datetime.datetime.strptime(to_date, '%Y-%m-%d')
        query = {
            'Date': {
                '$gte': from_date,
                '$lt': to_date
            },
            'ticker': ticker
        }
        self.logger.debug(f"Querying klines with query: {query}")
        query_result = self._collection.find(query)
        return list(query_result)

    def push(self, max_batch_size: int = 128) -> None:
        """Push local klines to MongoDB
        
        Args:
            from_date: (str) date string with format '%Y-%m-%d'. If None, use the earliest available date Default to None
            to_date: (str) date string with format '%Y-%m-%d'. If None, use the latest available date. Default to None
            max_batch_size: (int) the maximum batch size for each insert request. Default to 128
        """
        if not self.is_connected:
            raise RuntimeError("Please connect first or use with statement")
        kline_dir = self._load_price_data_dir()
        ticker_dirs = list(kline_dir.iterdir())

        n_klines = 0
        self.ensure_index()
        for date_dir in tqdm(ticker_dirs, total=len(ticker_dirs), desc="Pushing klines to MongoDB"):
            csv_path = date_dir / "interday" / f"{date_dir.name}_interday_1d.csv"
            if csv_path.exists():
                try:
                    kline_df = pd.read_csv(csv_path, parse_dates=['Date'])
                    kline_df['ticker'] = date_dir.name
                    kline_dicts = kline_df.to_dict(orient='records')
                    self.insert_many(kline_dicts, max_batch_size=max_batch_size)
                    n_klines += len(kline_dicts)
                except Exception as e:
                    self.logger.error(f"Failed to push klines for {date_dir.absolute()}: {e}, traceback: {traceback.format_exc()}")
        self.logger.info(f"Pushed {n_klines} klines to MongoDB")

    def connect(self) -> None:
        self._connector.connect()
        self._connector.select_database(self._db_name)
        self._collection: Collection = self._connector.database[self._collection_name]
        
    def disconnect(self) -> None:
        self._connector.disconnect()
        self._collection = None

    def _load_kline_mongodb_connection_string(self) -> str:
        load_dotenv()
        return os.getenv("FINICE_MONGODB_CONNECTION_STRING")

    def _load_price_data_dir(self) -> pathlib.Path:
        load_dotenv()
        return pathlib.Path(os.getenv("YFINANCE_PRICE_DATA_DIR"))

    def __enter__(self) -> FiniceMongoDBClient:
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
    

__all__ = [
    'FiniceMongoDBClient',
]
