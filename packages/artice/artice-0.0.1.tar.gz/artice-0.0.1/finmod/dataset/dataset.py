from __future__ import annotations

import json
import pathlib
import datetime
from typing import Tuple

import torch
from pydantic import BaseModel
import pytorch_lightning as pl
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.dataloader import default_collate

from utils import PathLike


class ArticleData(BaseModel):
    title: str
    provider: str
    article_id: str
    content: str
    related_ticker: str
    publish_time: datetime.datetime
    
    @classmethod
    def from_dict(cls, data_dict: dict) -> ArticleData:
        return cls(
            title=data_dict['title'],
            provider=data_dict['provider'],
            article_id=data_dict['article_id'],
            related_ticker=data_dict['ts_ticker'],
            content=data_dict['content'],
            publish_time=datetime.datetime.fromisoformat(data_dict['publish_time'])
        )
        
    def to_torch_dict(self) -> dict:
        """Convert the data to torch dict(torch does not support some types such as datetime, so we do the conversion here
        
        FIXME: you can customize how to convert the data here...
        """
        return {
            'title': self.title,
            'provider': self.provider,
            'article_id': self.article_id,
            'related_ticker': self.related_ticker,
            'content': self.content,
            'publish_time': self.publish_time.timestamp(),
        }
        
    def __repr__(self) -> str:
        return f"ArticleData(title={self.title}, provider={self.provider}, publish_time={self.publish_time})"
    
    def __str__(self) -> str:
        return f"ArticleData(title={self.title}, provider={self.provider}, publish_time={self.publish_time})"


class PriceData(BaseModel):
    ticker: str
    close_prices: list[float]
    day_shifts: list[int]
    dates: list[datetime.date]
    
    @classmethod
    def from_dict(cls, data_dict: dict) -> PriceData:
        return cls(
            ticker=data_dict['ts_ticker'],
            close_prices=data_dict['ts_close_prices'],
            day_shifts=data_dict['ts_day_shifts'],
            dates=[datetime.datetime.fromisoformat(d).date() for d in data_dict['ts_dates']]
        )
        
    def to_torch_tensor(self, dtype=torch.float32) -> torch.Tensor:
        """Convert the data to torch tensor
        
        Args:
            dtype (torch.dtype, optional): the data type of the tensor. Defaults to torch.float32.
            
        Returns:
            torch.Tensor: the time series tensor with shape (seq_len, num_features)
            
        FIXME: you can customize how to construct the time series tensor here...
        """
        # # Version 1: concat horizontally the close prices and day shifts
        # data = torch.tensor(self.close_prices + self.day_shifts, dtype=dtype).reshape(-1, 1)
        
        # Version 2: concat vertically the close prices and day shifts
        data = torch.tensor([self.close_prices, self.day_shifts], dtype=dtype)
        data = data.transpose(0, 1)
        return data
        
    def __repr__(self) -> str:
        return f"PriceData(ticker={self.ticker}, dates={self.dates[0]}-{self.dates[-1]})"
    
    def __str__(self) -> str:
        return f"PriceData(ticker={self.ticker}, dates={self.dates[0]}-{self.dates[-1]})"


class ArticeDataset(Dataset):
    """Artice: abbr for article-price pair

    Read data from local storage, the data should be stored in `artice_dir` in the format of json files.    
    """
    def __init__(self, artice_dir: PathLike):
        """
        Args:
            artice_dir (PathLike): the directory contains the article-price pair data
        """
        self.artice_dir = pathlib.Path(artice_dir)
        self.paired_data_dir = self.artice_dir / "pair"
        self.article_paths = list(self.paired_data_dir.iterdir())
        
    def __len__(self):
        return len(self.article_paths)
    
    def __getitem__(self, idx: int) -> Tuple[dict, torch.Tensor]:
        with open(self.article_paths[idx], 'r') as f:
            data = json.load(f)
        article_data = ArticleData.from_dict(data).to_torch_dict()
        price_data = PriceData.from_dict(data).to_torch_tensor()
        return article_data, price_data


class ArticeDataLoader(DataLoader):
    def __init__(self, dataset: ArticeDataset, batch_size: int = 32, shuffle: bool = True, num_workers: int = 0, **kwargs):
        if "collate_fn" in kwargs:
            kwargs.pop("collate_fn")
        super().__init__(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers, collate_fn=self._collate_fn, **kwargs)
        
    def _collate_fn(self, batch: list[Tuple[dict, dict]]) -> Tuple[dict[str, list], dict[str, torch.Tensor]]:
        # 1. articles
        articles, prices = zip(*batch)
        articles_collated = {
            "title": [a['title'] for a in articles],
            "content": [a['content'] for a in articles],
            "provider": [a['provider'] for a in articles],
            "publish_time": [a['publish_time'] for a in articles],
            "related_ticker": [a['related_ticker'] for a in articles],
        }
        # 2. time series collate
        prices_collated = default_collate(prices)
        prices_collated_dict = {
            "insample_y": prices_collated,
        }
        return articles_collated, prices_collated_dict


class ArticeDataModule(pl.LightningDataModule):

    def __init__(
        self,
        dataset: ArticeDataset,
        batch_size=32,
        valid_batch_size=1024,
        num_workers=0,
        drop_last=False,
        shuffle_train=True,
    ):
        super().__init__()
        self.dataset = dataset
        self.batch_size = batch_size
        self.valid_batch_size = valid_batch_size
        self.num_workers = num_workers
        self.drop_last = drop_last
        self.shuffle_train = shuffle_train

    def train_dataloader(self):
        loader = ArticeDataLoader(
            self.dataset,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            shuffle=self.shuffle_train,
            drop_last=self.drop_last,
        )
        return loader

    def val_dataloader(self):
        loader = ArticeDataLoader(
            self.dataset,
            batch_size=self.valid_batch_size,
            num_workers=self.num_workers,
            shuffle=False,
            drop_last=self.drop_last,
        )
        return loader

    def predict_dataloader(self):
        loader = ArticeDataLoader(
            self.dataset,
            batch_size=self.valid_batch_size,
            num_workers=self.num_workers,
            shuffle=False,
        )
        return loader


__all__ = [
    'PriceData',
    'ArticleData',
    'ArticeDataset',
    'ArticeDataLoader',
]
