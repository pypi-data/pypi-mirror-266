from __future__ import annotations

import os
import pathlib
import datetime
from typing import Optional

import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from pymongo.collection import Collection
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, BulkWriteError

from utils import MongoDBConnector, WithLogger, check_from_date_and_to_date_validity, today_str
from finart.yfinance_data.utils import read_article_json


class FinartMongoDBClient(WithLogger):
    def __init__(self, connection_string: Optional[str] = None):
        super().__init__()
        if not connection_string:
            connection_string = self._load_article_mongodb_connection_string()
        if not connection_string:
            raise ValueError(f"To enable FinartMongoDBClient, you must specify `FINART_MONGODB_CONNECTION_STRING` in `.env` file or system settings")
        self._connector = MongoDBConnector(connection_string=connection_string)
        self._db_name: str = "finart"
        self._collection_name: str = "yahoo_finance_articles"
        self._collection: Optional[Collection] = None

    @property
    def is_connected(self) -> bool:
        return self._connector.is_connected

    def ensure_index(self) -> None:
        if not self.is_connected:
            raise RuntimeError(f"Please connect first or use the with statement to control context.")
        
        self._collection.create_index([('fin_tickers', ASCENDING)], name='fin_tickers_index')
        self._collection.create_index([('publish_time', ASCENDING)], name='publish_time_index')
        self._collection.create_index([('fin_tickers', ASCENDING), ('publish_time', DESCENDING)], name='fin_tickers_publish_time_index')
        self._collection.create_index(
            [('article_id', ASCENDING)],
            name='article_id_index',
            unique=True
        )
        self._collection.create_index(
            'non_empty_fin_tickers',
            name='non_empty_fin_tickers_index',
        )

    def insert(self, article: dict, duplicated_ok: bool = True):
        """Insert one article to MongoDB database

        Args:
            article: (dict) the article data dict
            duplicated_ok: (bool) ignore duplicated key error. Default to True
        """
        if not self.is_connected:
            raise RuntimeError("Please connect first or use with statement")
        try:
            result = self._collection.insert_one(article)
            return result
        except DuplicateKeyError as e:
            if not duplicated_ok:
                raise e
        
    def insert_many(self, articles: list[dict], duplicated_ok: bool = True, max_batch_size: int = 128):
        if not self.is_connected:
            raise RuntimeError("Please connect first or use with statement")

        for batch_start in range(0, len(articles), max_batch_size):
            try:
                article_batch = articles[batch_start:batch_start + max_batch_size]
                self._collection.insert_many(article_batch)
            except DuplicateKeyError as e:
                if not duplicated_ok:
                    raise e
                continue
            except BulkWriteError as e:
                if not duplicated_ok:
                    raise e
                continue

    def query_by_date_range(self, from_date: Optional[str] = None, to_date: Optional[str] = None, ticker: Optional[str] = None, limit: int = 0, required_fin_tickers: Optional[bool] = None) -> list[dict]:
        """
        Args:
            from_date: (str) date string with format '%Y-%m-%d'
            to_date: (str) date string with format '%Y-%m-%d'
            limit: (int) limit of results, if 0, no limits
            
        Returns:
            list[dict]: list of articles
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
            'publish_time': {
                '$gte': from_date,
                '$lt': to_date
            },
        }
        if ticker:
            query['fin_tickers'] = ticker
        if required_fin_tickers is not None:
            query['non_empty_fin_tickers'] = required_fin_tickers
        self.logger.debug(f"Querying articles with query: {query}")
        query_result = self._collection.find(query)
        if limit > 0:
            query_result = query_result.limit(limit)
        return list(query_result)

    def push(self, from_date: Optional[str] = None, to_date: Optional[str] = None, max_batch_size: int = 128) -> None:
        """Push local articles to MongoDB
        
        Args:
            from_date: (str) date string with format '%Y-%m-%d'. If None, use the earliest available date Default to None
            to_date: (str) date string with format '%Y-%m-%d'. If None, use the latest available date. Default to None
            max_batch_size: (int) the maximum batch size for each insert request. Default to 128
        """
        if not self.is_connected:
            raise RuntimeError("Please connect first or use with statement")
        article_dir = self._load_article_data_dir() / "articles/sitemap/parsed"
        all_date_dirs = sorted(article_dir.glob('*'))
        if from_date is None:
            from_date = all_date_dirs[0].name
        if to_date is None:
            to_date = all_date_dirs[-1].name
        from_date = max(from_date, all_date_dirs[0].name)
        to_date = min(to_date, all_date_dirs[-1].name)
        from_date, to_date = check_from_date_and_to_date_validity(from_date_str=from_date, to_date_str=to_date)
        date_dirs = [article_dir / d.strftime('%Y-%m-%d') for d in pd.date_range(from_date, to_date, freq='D') if (article_dir / d.strftime('%Y-%m-%d')).exists()]

        n_articles = 0
        self.ensure_index()
        for date_dir in tqdm(date_dirs, total=len(date_dirs), desc="Pushing articles to MongoDB"):
            json_files = date_dir.glob('*.json')
            article_dicts = [read_article_json(f) for f in json_files]
            n_articles += len(article_dicts)
            self.insert_many(article_dicts, max_batch_size=max_batch_size)
        self.logger.info(f"Pushed {n_articles} articles to MongoDB")

    def connect(self) -> None:
        self._connector.connect()
        self._connector.select_database(self._db_name)
        self._collection: Collection = self._connector.database[self._collection_name]
        
    def disconnect(self) -> None:
        self._connector.disconnect()
        self._collection = None

    def _load_article_mongodb_connection_string(self) -> str:
        load_dotenv()
        return os.getenv("FINART_MONGODB_CONNECTION_STRING")

    def _load_article_data_dir(self) -> pathlib.Path:
        load_dotenv()
        return pathlib.Path(os.getenv("YFINANCE_ARTICLE_DATA_DIR"))

    def __enter__(self) -> FinartMongoDBClient:
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
    

__all__ = [
    'FinartMongoDBClient',
]
