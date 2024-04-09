import pytz
import pathlib
from typing import Optional

import pandas as pd
from tqdm import tqdm
import yfinance as yf

from constant import valid_nyse_stock_list
from finice.utils import PathLike, Period, read_daily_kline_yfinance, yf_download


tz = pytz.timezone("America/New_York")
"""timezone used to download data from Yahoo Finance"""


class YFPriceDownloader:
    """YFinance Market Data Downloader
    
    
    Example Usage:
    ```python
    downloader = YFPriceDownloader()
    
    # download the daily kline for 'AAPL' and 'TSLA' for the last 3 years, default concurrency is 6
    downloader.download_histories(["AAPL", "TSLA"], period="3y")
    
    # download all available history data for each ticker enlisted in nyse, with only 3 concurrent worker
    downloader.download_all_histories(period="max", concurrency=3)
    ```
    
    After downloading the data, you can use `YFinanceReader` to read the data, like:
    ```python
    reader = YFinanceReader()
    df = reader.read("AAPL", from_date="2021-01-01", to_date="2021-12-31")
    ```
    """
    import ray
    
    _5m_period_max = '60d'
    _1m_period_max = '7d'
    
    def __init__(self, data_dir: Optional[PathLike] = None):
        """
        Args:
            data_dir (Optional[PathLike], optional): data directory. Defaults to None, i.e. load from environment variables.
        """
        if not data_dir:
            data_dir = self._load_data_dir_from_env()
        self.data_dir:pathlib.Path = data_dir
 
    def download_all_histories(self, period: str = 'max', concurrency: int = 6, skip_if_downloaded: bool = False) -> None:
        """Download All available history data for each ticker enlisted in nyse, see the list at `constant.valid_nyse_stock_list`
        
        Args:
            period (str, optional): Download period. Defaults to 'max', you can specify '10d', '3w', '1M', '1y', etc...
            concurrency (int, optional): Max number of concurrent downloads. Defaults to 5.
            skip_if_downloaded (bool, optional): Skip the download if the data is already downloaded, If true, then you may have only the old data. Defaults to False.
        """
        self.download_histories(valid_nyse_stock_list, period=period, concurrency=concurrency, skip_if_downloaded=skip_if_downloaded)
        
    def download_histories(self, tickers: list[str], period: str = 'max', concurrency: int = 6, skip_if_downloaded: bool = False) -> None:
        """Download history data for a list of tickers
        
        Args:
            tickers (list[str]): The list of ticker symbols
            period (str, optional): Download period. Defaults to 'max'.
            concurrency (int, optional): Max number of concurrent downloads. Defaults to 5.
            skip_if_downloaded (bool, optional): Skip the download if the data is already downloaded, If true, then you may have only the old data. Defaults to False.
        """
        import ray
        ray.init(num_cpus=concurrency)

        with tqdm(total=len(tickers)) as progress_bar:
            result_ids = [self.download_history_remote.remote(self, ticker, period, skip_if_downloaded) for ticker in tickers]

            for i in range(len(tickers)):
                done_id, result_ids = ray.wait(result_ids)
                ray.get(done_id[0])
                ticker = tickers[i]
                progress_bar.update(1)
                progress_bar.set_description(f"Downloading {ticker}...")

        ray.shutdown()
    
    def download_history(self, ticker: str, period: str = 'max', skip_if_downloaded: bool = False) -> None:
        """Download history data for a single ticker
        
        Args:
            ticker (str): The ticker symbol
            period (str, optional): Download period. Defaults to 'max'.
            skip_if_downloaded (bool, optional): Skip the download if the data is already downloaded, If true, then you may have only the old data. Defaults to False.
        """
        # 1. Check the input parameters
        period: Period = Period.parse(period)
        tk = self._check_ticker_availability(ticker)
        
        # 2. Constrains the period to obey the Yahoo Finance API
        period_1d_yf = period.to_yfinance_repr()
        period_5m_yf = min(Period.parse('60d'), period).to_yfinance_repr()
        period_1m_yf = min(Period.parse('7d'), period).to_yfinance_repr()

        # 3. Download and organize interday data        
        tk_dir = self.data_dir / ticker
        final_path = tk_dir / "interday" / f"{ticker}_interday_1d.csv"
        if skip_if_downloaded and final_path.exists():
            return
        
        df_1d = yf_download(ticker=ticker, period=period_1d_yf)
        # df_1d = tk.history(period=period_1d_yf, interval="1d")
        
        # Filter out empty data
        if len(df_1d) == 0:
            return
        
        try:
            tk_dir.mkdir(parents=True, exist_ok=True)
            df_1d.to_csv(tk_dir / f"{ticker}_history_1d.csv")
            self._organize_interday_history_data(ticker=ticker)
            (tk_dir / f"{ticker}_history_1d.csv").unlink()
        # FIXME: do we need to manually process the special names such like CON(the windows reserved specifier)?
        except NotADirectoryError:
            print(f"[Error] {tk_dir} is not a valid windows directory, so we abandon this ticker...")
            pass
        
        # # 4. TODO: Download and organize intraday data
        # tk.history(period=period_5m_yf, interval="5m").to_csv(tk_dir / f"{ticker}_history_5m.csv")
        # tk.history(period=period_1m_yf, interval="1m").to_csv(tk_dir / f"{ticker}_history_1m.csv")
        # self._organize_intraday_history_data(ticker=ticker)
           
    @ray.remote
    def download_history_remote(self, ticker, period='max', skip_if_downloaded=False):
        return self.download_history(ticker, period, skip_if_downloaded)
               
    def _check_ticker_availability(self, ticker: str):
        tk = yf.Ticker(ticker)
        if not tk:
            raise ValueError(f"Ticker {ticker} is not available in Yahoo Finance, it may be invalid or delisted.")
        return tk
        
    def _load_data_dir_from_env(self) -> pathlib.Path:
        from finice.yfinance_data.config import finice_yfinance_config
        if not finice_yfinance_config.data_dir:
            raise ValueError(f"YFINANCE_PRICE_DATA_DIR is not set, please set it in your environment variables or in the .env file, or just pass it to the constructor.")
        return finice_yfinance_config.data_dir

    # TODO: how to get intraday data from yfinance with missing period checking?
    def _organize_intraday_history_data(self, ticker: str):
        ticker_dir = self.data_dir / ticker
        delta_1m_csv = ticker_dir / f"{ticker}_history_1m.csv"
        delta_5m_csv = ticker_dir / f"{ticker}_history_5m.csv"
        
        raise NotImplementedError("Organize intra-day history data is not implemented yet.")
        
    def _organize_interday_history_data(self, ticker: str) -> pathlib.Path:
        ticker_dir = self.data_dir / ticker
        delta_csv = ticker_dir / f"{ticker}_history_1d.csv"
        persistent_csv = ticker_dir / "interday" / f"{ticker}_interday_1d.csv"
        
        delta_df = read_daily_kline_yfinance(delta_csv)
        if persistent_csv.exists():
            persistent_df = read_daily_kline_yfinance(persistent_csv)
            last_date = persistent_df.iloc[-1]["Date"]
            delta_df = delta_df[delta_df["Date"] > last_date]
            if not delta_df.empty:
                persistent_df = pd.concat([persistent_df, delta_df], ignore_index=True)
                persistent_df.to_csv(persistent_csv, index=False)
        else:
            persistent_csv.parent.mkdir(parents=True, exist_ok=True)
            delta_df.to_csv(persistent_csv, index=False)
            
        return persistent_csv


__all__ = [
    'YFPriceDownloader',
]
