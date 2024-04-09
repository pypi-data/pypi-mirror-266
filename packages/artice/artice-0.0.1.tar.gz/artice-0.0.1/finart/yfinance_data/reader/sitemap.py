import json
import random
import pathlib
import datetime
from itertools import chain
from typing import Optional, Union

import pandas as pd

from utils import WithLogger, date_from_str
from finart.yfinance_data.utils import read_article_json

from finart.yfinance_data.db import FinartMongoDBClient
from finart.yfinance_data.config import finart_yfinance_config


class YFArticleLocalReader(WithLogger):
    """Yahoo Finance Article Reader, read from local json files.
    
    You need to configure `YFINANCE_ARTICLE_DATA_DIR` to enable this reader
    """
    def __init__(self):
        super().__init__()
        self.article_dir = finart_yfinance_config.sitemap_article_json_dir

    def read_date_range(self, from_date: Optional[Union[str, datetime.date]] = None, to_date: Optional[Union[str, datetime.date]] = None, limit: int = -1, as_df: bool = True) -> Union[list[dict], pd.DataFrame]:
        if from_date and isinstance(from_date, str):
            from_date = date_from_str(from_date)
        if to_date and isinstance(to_date, str):
            to_date = date_from_str(to_date)
        article_date_dirs = sorted(list(self.article_dir.iterdir()))
        earliest_date = date_from_str(article_date_dirs[0].name)
        latest_date = date_from_str(article_date_dirs[-1].name)
        if from_date is None:
            from_date = earliest_date
        else:
            from_date = max(from_date, earliest_date)
        if to_date is None:
            to_date = latest_date
        else:
            to_date = min(to_date, latest_date)
        
        included_dir = []
        for d in pd.date_range(from_date, to_date):
            d_dir = self.article_dir / d.strftime("%Y-%m-%d")
            if d_dir.exists():
                included_dir.append(d_dir)
        
        article_paths = list(chain(*[list(d.iterdir()) for d in included_dir]))
        random.shuffle(article_paths)
        if limit > 0:
            article_paths = article_paths[:limit]
        if len(article_paths) == 0:
            self.logger.warning(f"No article found in the date range {from_date} to {to_date}.")
            return [] if not as_df else pd.DataFrame()
            
        article_dict_list = [read_article_json(p) for p in article_paths]
        if as_df:
            return pd.DataFrame(article_dict_list)
        else:
            return article_dict_list
    
    def read_on_date(self, d: Union[str, datetime.date], limit: int = -1, as_df: bool = True) -> Union[list[dict], pd.DataFrame]:
        return self.read_date_range(from_date=d, to_date=d, limit=limit, as_df=as_df)
    
    def read_random(self, n_dates: int = 3, n_articles_per_date: int = 5, as_df: bool = True) -> Union[list[dict], pd.DataFrame]:
        sub_dirs = random.sample(list(self.article_dir.iterdir()), n_dates)
        article_paths = []
        for d in sub_dirs:
            article_paths.extend(random.sample(list(d.iterdir()), n_articles_per_date))
        article_dict_list = [json.load(open(p, "r", encoding="utf-8")) for p in article_paths]
        if as_df:
            return pd.DataFrame(article_dict_list)
        else:
            return article_dict_list

    @classmethod
    def read_fp(fp: Union[str, pathlib.Path], as_df: bool = True) -> Union[list[dict], pd.DataFrame]:
        article_dict = read_article_json(fp)
        if as_df:
            return pd.DataFrame([article_dict])
        else:
            return [article_dict]


class YFArticleMongoReader(WithLogger):
    def __init__(self):
        super().__init__()
        self.client = FinartMongoDBClient()

    def read(self, from_date: Optional[str] = None, to_date: Optional[str] = None, ticker: Optional[str] = None, limit: int = 100, required_fin_tickers: Optional[bool] = None, as_df: bool = True) -> Optional[Union[list[dict], pd.DataFrame]]:
        """Read articles from MongoDB
        
        Args:
            from_date: (str) date string with format '%Y-%m-%d'
            to_date: (str) date string with format '%Y-%m-%d'
            ticker: (str) ticker symbol
            limit: (int) limit of results, if 0, no limits
            required_fin_tickers: (bool) only return articles with financial tickers
            as_df: (bool) return as DataFrame if True

        Returns:
            Union[list[dict], pd.DataFrame]: list of articles
        """
        with self.client:
            articles = self.client.query_by_date_range(from_date=from_date, to_date=to_date, ticker=ticker, limit=limit, required_fin_tickers=required_fin_tickers)
        if as_df:
            df = pd.DataFrame(articles).reset_index(drop=True)
            if len(df) == 0:
                # self.logger.warning(f"No article found in the date range {from_date} to {to_date}.")
                return None
            return df
        else:
            return articles if len(articles) > 0 else None

class YFArticlePreprocessor:
    @classmethod
    def with_fin_tickers(cls, articles: Union[list[dict], pd.DataFrame]) -> Union[list[dict], pd.DataFrame]:
        if isinstance(articles, pd.DataFrame):
            articles['has_fin'] = articles['fin_tickers'].apply(lambda x: len(x) > 0)
            articles = articles[articles['has_fin']].reset_index(drop=True)
            articles.drop(columns=['has_fin'], inplace=True)
            return articles
        else:
            return [article for article in articles if len(article['fin_tickers']) > 0]
        

__all__ = [
    'YFArticleLocalReader',
    'YFArticleMongoReader',
    'YFArticlePreprocessor',
]
    