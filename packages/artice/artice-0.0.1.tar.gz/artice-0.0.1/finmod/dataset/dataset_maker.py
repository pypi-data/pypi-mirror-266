import json
import random
import pathlib

import pandas as pd
from tqdm import tqdm
from bson import ObjectId

from finice import YFPriceMongoReader
from finart import YFArticleMongoReader
from utils import PathLike, check_or_make_dir, WithLogger, zip_dir


def json_encode(data_dict: dict) -> dict:
    """Encode the dict to json serializable format"""
    for k, v in data_dict.items():
        if isinstance(v, pd.Timestamp):
            # use isoformat
            data_dict[k] = v.isoformat()
        if isinstance(v, pathlib.Path):
            data_dict[k] = str(v)
        if isinstance(v, ObjectId):
            data_dict[k] = str(v)
    return data_dict


class DatasetMaker(WithLogger):
    """Make a dataset from finart and finice(use MongoDB data)

    If we need 
    
    It should cover `N` articles and `N_p` prices(empirically, `N_p` ~= 1.4 * `N` in our yahoo finance dataset)
    
    suppose each article has `C` corresponding tickers.
    
    Theoretically, we can construct `N * C` positive pairs and `N * (N_p - C)` negative pairs.

    We only care about positive pairs, because in contrast learning, negative pairs are usually built on the fly using batch    
    """
    def __init__(self, n_samples: int, seed: int = 42):
        """
        Args:
            n_samples: (int) how many samples(or pairs) we make
            seed: (int) the random seed to generate the dataset
        """
        super().__init__()
        assert n_samples > 0, "n_samples must be a positive integer"
        assert seed > 0, "seed must be a positive integer"
        self._n_samples = n_samples
        """how many positive pairs should we make"""
        self._seed = seed
        """the random seed to generate the dataset"""
        self._price_reader = YFPriceMongoReader()
        self._article_reader = YFArticleMongoReader()
        self._decide_n_articles()
        random.seed(self._seed)
        
    def _decide_n_articles(self) -> None:
        """Decide how many articles should be covered to construct the dataset(just a empherical rule)"""
        self._n_articles = int(self._n_samples * 0.75)
        """(int) how many article records should be covered to construct the dataset"""
        
    def make(self, output_dir: PathLike, zipped_after_make: bool = True, history_winsize: int = 45, future_winsize: int = 15) -> None:
        """
        Args:
            output_dir: (PathLike) the output directory to save the dataset
            zipped_after_make: (bool) whether to zip the output directory after making the dataset
            history_winsize: (int) how many days before the publish date should be included in the price data
            future_winsize: (int) how many days after the publish date should be included in the price data
        """
        # 0. input validity
        assert history_winsize > 0, "history_winsize must be a positive integer"
        assert future_winsize > 0, "future_winsize must be a positive integer"
        output_dir = pathlib.Path(output_dir)
        check_or_make_dir(output_dir)
        zipped_path = output_dir.parent / f"{output_dir.name}.zip"
        
        # 1. fetch articles
        article_df = self._fetch_articles()
        
        data_dict_list = []
        self.logger.info(f"Start to scan the articles for constructing dataset...")
        for _, row in tqdm(article_df.iterrows(), total=len(article_df), desc="Scanning articles..."):
            data_dict = row.to_dict()
            data_dict.pop('in_article_links')
            tickers: list[str] = data_dict.pop('fin_tickers')
            for ticker in tickers:
                try:
                    publish_date = row['publish_time'].date()
                    price_df = self._price_reader.read_around_date(
                        ticker=ticker,
                        target_date = publish_date.strftime("%Y-%m-%d"),
                        history_winsize = history_winsize,
                        future_winsize = future_winsize,
                    )
                    close_prices = price_df['Close'].to_list()
                    day_shifts = price_df['Date'].apply(lambda x: (x.date() - publish_date).days).to_list()
                    data_dict['ts_ticker'] = ticker
                    data_dict['ts_dates'] = [d.isoformat() for d in price_df['Date'].to_list()]
                    data_dict['ts_close_prices'] = close_prices
                    data_dict['ts_day_shifts'] = day_shifts
                    
                    # append the data_dict to the list
                    data_dict_list.append(data_dict.copy())
                except Exception as e:
                    # If the price data is not found or not enough, just skip this sample
                    # print(f"Error when fetching price data for {ticker}: {e}, the price data for {ticker} will be skipped. traceback: {traceback.format_exc()}")
                    continue

        # shuffle and truncate the data_dict_list
        self.logger.info(f"Got {len(data_dict_list)} data_dict_list, start to shuffle and truncate to {self._n_samples} samples...")
        random.shuffle(data_dict_list)
        data_dict_list = data_dict_list[:self._n_samples]
        if len(data_dict_list) < self._n_samples:
            self.logger.warning(f"Only {len(data_dict_list)}  pairs are constructed, less than the expected {self._n_samples}")
        paired_dir = output_dir / "pair"
        check_or_make_dir(paired_dir)
        self.logger.info(f"Save {len(data_dict_list)} paired data to {paired_dir}")
        # sort data_dict_list by 'article_id'
        data_dict_list = sorted(data_dict_list, key=lambda x: x['article_id'])
        for i, data_dict in tqdm(enumerate(data_dict_list), desc="Saving paired data..."):
            json_path = paired_dir / f"pair_{data_dict['article_id']}_{data_dict['ts_ticker']}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_encode(data_dict), f)
        
        # zip if needed
        if zipped_after_make:
            self.logger.info(f"Zipping the output directory to {zipped_path}")
            zip_dir(output_dir, zipped_path)
            
    def _fetch_articles(self) -> pd.DataFrame:
        """Fetch articles from the MongoDB"""
        # TODO: random sampling? now we just always fetch the first N articles
        article_df = self._article_reader.read(limit=self._n_articles, required_fin_tickers=True)
        return article_df
        

def make_dataset(n_samples: int, output_dir: PathLike, zipped_after_make: bool = True, history_winsize: int = 45, future_winsize: int = 15) -> pathlib.Path:
    """Make a dataset from finart and finice(use MongoDB data)

    Args:
        n_samples: (int) how many samples(or pairs) we make
        output_dir: (PathLike) the output directory to save the dataset
        zipped_after_make: (bool) whether to zip the output directory after making the dataset
        history_winsize: (int) how many days before the publish date should be included in the price data
        future_winsize: (int) how many days after the publish date should be included in the price data

    Returns:
        (pathlib.Path) the path to the output directory
    """
    maker = DatasetMaker(n_samples=n_samples)
    maker.make(output_dir=output_dir, zipped_after_make=zipped_after_make, history_winsize=history_winsize, future_winsize=future_winsize)
    return pathlib.Path(output_dir)


__all__ = [
    "DatasetMaker",
    "make_dataset",
]
