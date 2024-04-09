import pathlib
import datetime
import warnings
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from finice.utils import KlineInterval
from finice.tardis_data.raw import TardisRawDownloader
from finice.tardis_data.utils import Exchange, DataType, get_gzip_file_relpath


class TardisKlineSynthesizer:
    """Synthesize kline data from trades and book ticker data"""
    def __init__(self, data_dir: Optional[str] = None):
        if not data_dir:
            data_dir = self._load_data_dir_from_env()
        self.data_dir = pathlib.Path(data_dir)
    
    def synthesize(
        self,
        exchange: Exchange,
        symbols: list[str],
        from_date: str,
        to_date: str,
        concurrent: int = 4,
    ) -> None:
        with ThreadPoolExecutor(max_workers=concurrent) as executor:
            task_args = [
                (exchange, symbol, date.strftime("%Y-%m-%d"))
                for symbol in symbols
                for date in pd.date_range(from_date, to_date)
            ]
            futures = {
                executor.submit(self.synthesize_one, *args): args
                for args in task_args
            }
            for future in as_completed(futures):
                args = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f'[{self.__class__.__name__}] Error occurred for args: {args}: {e}')
    
    def synthesize_one(
        self,
        exchange: Exchange,
        symbol: str,
        date: str,
    ) -> pathlib.Path:
        output_csv_path = self.data_dir / "kline" / get_gzip_file_relpath(exchange=exchange, data_type=DataType.KLINE, date=date, symbol=symbol).strip(".gz")
        if output_csv_path.exists():
            print(f"[{self.__class__.__name__}] Kline data already exists for {exchange.value} {symbol} on {date}. Skipping...")
            return output_csv_path
        
        trades_csv_path = self.data_dir / "raw" / get_gzip_file_relpath(exchange=exchange, data_type=DataType.TRADES, date=date, symbol=symbol).strip(".gz")
        book_ticker_csv_path = self.data_dir / "raw" / get_gzip_file_relpath(exchange=exchange, data_type=DataType.BOOK_TICKER, date=date, symbol=symbol).strip(".gz")
        missing_data_types = []
        if not trades_csv_path.exists():
            missing_data_types.append(DataType.TRADES)
        if not book_ticker_csv_path.exists():
            missing_data_types.append(DataType.BOOK_TICKER)
        if missing_data_types:
            print(f"[{self.__class__.__name__}] Missing data types: {missing_data_types} for {exchange.value} {symbol} on {date}. Downloading...")
            TardisRawDownloader(data_dir=self.data_dir).download_and_unzip(
                exchange=exchange,
                data_types=missing_data_types,
                symbols=[symbol],
                from_date=date,
                to_date=date,
            )
            
        print(f"[{self.__class__.__name__}] Reading data for kline({exchange.value} {symbol} on {date})...")
        start_dt, end_dt = pd.Timestamp(date), pd.Timestamp(date) + datetime.timedelta(days=1)
        trades_df = pd.read_csv(trades_csv_path, usecols=['timestamp', 'amount']).sort_values(by='timestamp')
        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'], unit='us')
        trades_df = trades_df[(trades_df['timestamp'] >= start_dt) & (trades_df['timestamp'] < end_dt)]
        book_ticker_df = pd.read_csv(book_ticker_csv_path, usecols=['timestamp', 'bid_price', 'ask_price']).sort_values(by='timestamp')
        book_ticker_df['timestamp'] = pd.to_datetime(book_ticker_df['timestamp'], unit='us')
        book_ticker_df = book_ticker_df[(book_ticker_df['timestamp'] >= start_dt) & (book_ticker_df['timestamp'] < end_dt)]

        print(f"[{self.__class__.__name__}] Synthesizing kline data({exchange.value} {symbol} on {date})...")
        trades_resampled = trades_df.resample('s', on='timestamp').amount.sum().reset_index()
        book_ticker_resampled = book_ticker_df.resample('s', on='timestamp').agg({
            'bid_price': 'first',
            'ask_price': 'last'
        }).reset_index()

        all_seconds = pd.date_range(start=start_dt, periods=86400, freq='s')
        if len(trades_df) < 86400:
            warnings.warn(f"Missing data for {exchange.value} {symbol} on {date} in trades data, filling with 0. len(trades_df)={len(trades_df)}")
            trades_resampled.set_index('timestamp', inplace=True)
            trades_resampled = trades_resampled.reindex(all_seconds, fill_value=0).reset_index().rename(columns={"index": "timestamp"})
        if len(book_ticker_df) < 86400:
            warnings.warn(f"Missing data for {exchange.value} {symbol} on {date} in book ticker data, filling with ffill. len(book_ticker_df)={len(book_ticker_df)}")
            book_ticker_resampled.set_index('timestamp', inplace=True)
            book_ticker_resampled = book_ticker_resampled.reindex(all_seconds, method='ffill').reset_index().rename(columns={"index": "timestamp"})
        
        # 合并数据为 kline_df
        kline_df = trades_resampled.merge(book_ticker_resampled, on='timestamp', how='outer').ffill()
        kline_df['open'] = kline_df['bid_price']
        kline_df['close'] = kline_df['ask_price']
        kline_df['high'] = kline_df['open']  # 这里简化处理，实际可能需要额外数据来计算
        kline_df['low'] = kline_df['open']  # 同上
        kline_df['volume'] = kline_df['amount']
        kline_df = kline_df.drop(['amount', 'bid_price', 'ask_price'], axis=1)
        kline_df.rename(columns={'timestamp': 'open_timestamp'}, inplace=True)
        kline_df['close_timestamp'] = kline_df['open_timestamp'] + pd.Timedelta(seconds=1)

        # 确保输出为86400行, 并且输出到 output_csv_path
        assert len(kline_df) == 86400
        print(f"[{self.__class__.__name__}] Saving synthesized kline data({exchange.value} {symbol} on {date}) to {output_csv_path}...")
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        kline_df.to_csv(output_csv_path, index=False)
        
        return output_csv_path
    
    def _load_data_dir_from_env(self) -> pathlib.Path:
        from .config import tardis_config
        if not tardis_config.data_dir:
            raise ValueError(f"TARDIS_DATA_DIR is not set, please set it in your environment variables or in the .env file, or just pass it to the constructor.")
        return tardis_config.data_dir


class TardisKlineReader:
    """Read kline data from the data directory"""
    def __init__(self, data_dir: Optional[str] = None):
        if not data_dir:
            data_dir = self._load_data_dir_from_env()
        self.data_dir = pathlib.Path(data_dir)
    
    def read(self, exchange: Exchange, symbol: str, from_date: str, to_date: str, interval: str = '1s') -> pd.DataFrame:
        """Read kline data with granual level `interval`
        
        Args:
            exchange (Exchange): exchange, e.g. Exchange.BINANCE
            symbol (str): symbol, e.g. 'btcusdt'
            from_date (str): start date, e.g. '2021-01-01', inclusive
            to_date (str): end date, e.g. '2021-01-01', inclusive
            interval (str): kline interval, default to '1s', support 's', 'm', 'h', 'd', 'w', 'M', 'y'
        
        Returns:
            pd.DataFrame: kline data
        """
        # 1. find all filepaths, check the availability
        kline_csv_paths = []
        not_found_csv_paths = []
        for date in pd.date_range(from_date, to_date):
            kline_csv_path = self.data_dir / "kline" / get_gzip_file_relpath(exchange=exchange, data_type=DataType.KLINE, date=date.strftime("%Y-%m-%d"), symbol=symbol).strip(".gz")
            if kline_csv_path.exists():
                kline_csv_paths.append(kline_csv_path)
            else:
                not_found_csv_paths.append(kline_csv_path)
        if not_found_csv_paths:
            raise FileNotFoundError(f"Kline data not found for {exchange.value} {symbol} on {not_found_csv_paths}")
        
        # 2. read and concat
        kline_dfs = [pd.read_csv(kline_csv_path) for kline_csv_path in kline_csv_paths]
        return pd.concat(kline_dfs, ignore_index=True)

    def read_one(self, exchange: Exchange, symbol: str, date: str) -> pd.DataFrame:
        kline_csv_path = self.data_dir / "kline" / get_gzip_file_relpath(exchange=exchange, data_type=DataType.KLINE, date=date, symbol=symbol).strip(".gz")
        if not kline_csv_path.exists():
            raise FileNotFoundError(f"Kline data not found for {exchange.value} {symbol} on {date}")
        return pd.read_csv(kline_csv_path)
    
    def _load_data_dir_from_env(self) -> pathlib.Path:
        from .config import tardis_config
        if not tardis_config.data_dir:
            raise ValueError(f"TARDIS_DATA_DIR is not set, please set it in your environment variables or in the .env file, or just pass it to the constructor.")
        return tardis_config.data_dir


__all__ = [
    'KlineInterval',
    'TardisKlineReader',
    'TardisKlineSynthesizer',
]
