import asyncio
import pathlib
from typing import Optional
from datetime import datetime, timedelta

import aiohttp
from tardis_dev import datasets, get_exchange_details

from finice.utils import PathLike, unzip
from finice.tardis_data.utils import Exchange, DataType, get_gzip_file_relpath

default_timeout = aiohttp.ClientTimeout(total=30 * 60)
"""default timeout for the download request, 30 minutes"""

def get_filename(exchange: str, data_type: str, date: datetime, symbol: str, format: str):
    """filename handler for `tardis_dev.datasets.download` method"""
    exchange = Exchange.from_value(exchange)
    data_type = DataType.from_value(data_type)
    return get_gzip_file_relpath(exchange, data_type, date, symbol)


class TardisRawDownloader:
    """Download raw zipped data from tardis.dev(tardis api key is required)
    
    For api key setup, you can choose any of the following methods:
    - Set `TARDIS_API_KEY` in your environment variables
    - Set `TARDIS_API_KEY` in the project root .env file
    - Pass the api key to the constructor, i.e. `downloader = TardisDownloader(api_key="your_api_key")`
    
    Example Usage:
    ```python
    downloader = TardisRawDownloader()
    # download the raw zipped files
    downloader.download_and_unzip(...)
    ```
    """
    def __init__(self, api_key: Optional[str] = None, data_dir: Optional[PathLike] = None):
        """
        Args:
            api_key (Optional[str], optional): tardis api key. Defaults to None, i.e. load from environment variables.
            data_dir (Optional[PathLike], optional): data directory. Defaults to None, i.e. load from environment variables.
        """
        if not api_key:
            api_key = self._load_api_key_from_env()
        if not data_dir:
            data_dir = self._load_data_dir_from_env()
        self.tardis_api_key: str = api_key
        self.data_dir:pathlib.Path = data_dir
    
    def download_and_unzip(
        self,
        exchange: Exchange,
        data_types: list[DataType],
        symbols: list[str],
        from_date: str,
        to_date: str,
        timeout = default_timeout,
        concurrency_download = 5,
        concurrency_unzip = 8,
        delete_zipped = True,
    ) -> None:
        """Download raw zipped data from tardis.dev and unzip them
        
        Args:
            exchange (Exchange): target exchange market
            data_types (list[DataType]): target data types
            symbols (list[str]): accepted symbols, e.g. ["ethusdt"]
            from_date (str): start date in format "YYYY-MM-DD"
            to_date (str): end date in format "YYYY-MM-DD"
            timeout (aiohttp.ClientTimeout, optional): timeout for the request. Defaults to default_timeout.
            concurrency_download (int, optional): number of concurrent download requests. Defaults to 5.
            concurrency_unzip (int, optional): number of concurrent unzip operations. Defaults to 8.
            delete_zipped (bool, optional): whether to delete the zipped files after unzipping. Defaults to True.
        """
        self.download(
            exchange=exchange,
            data_types=data_types,
            symbols=symbols,
            from_date=from_date,
            to_date=to_date,
            timeout=timeout,
            concurrency=concurrency_download,
        )
        self.unzip(concurrent=concurrency_unzip, delete_zipped=delete_zipped)
        
    def download(
        self,
        exchange: Exchange,
        data_types: list[DataType],
        symbols: list[str],
        from_date: str,
        to_date: str,
        timeout = default_timeout,
        concurrency = 5,
    ) -> None:
        """Download raw zipped data from tardis.dev

        Args:
            exchange (Exchange): target exchange market
            data_types (list[DataType]): target data types
            symbols (list[str]): accepted symbols, e.g. ["ethusdt"]
            from_date (str): start date in format "YYYY-MM-DD"
            to_date (str): end date in format "YYYY-MM-DD"
            timeout (aiohttp.ClientTimeout, optional): timeout for the request. Defaults to default_timeout.
            concurrency (int, optional): number of concurrent requests. Defaults to 5.
        """
        # check compatibility of data types and exchange
        self._validate_data_types(exchange, data_types)
        from_date = datetime.fromisoformat(from_date).date()
        to_date = datetime.fromisoformat(to_date).date()
        if to_date > datetime.now().date() + timedelta(days=1):
            raise ValueError(f"to_date {to_date} is greater than tomorrow: {datetime.now().date() + timedelta(days=1)}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # check the symbol existence and date range validity
            exchange_details = get_exchange_details(exchange.value)
            symbol_idxes = self._check_symbol_existence(symbols, exchange_details)
            symbol_download_metadatas = self._construct_download_metadatas(symbol_idxes, from_date, to_date, exchange_details)

            # downloading
            for download_metadata in symbol_download_metadatas:
                print(f"[{self.__class__.__name__}] ------ download with metadata: {download_metadata}...")
                datasets.download(
                    exchange=exchange.value,
                    data_types=[data_type.value for data_type in data_types],
                    symbols=[download_metadata['id']],
                    from_date=download_metadata['from_date'],
                    to_date=download_metadata['to_date'],
                    api_key=self.tardis_api_key,
                    download_dir=self.data_dir / "temp/zipped/",
                    get_filename=get_filename,
                    timeout=timeout,
                    concurrency=concurrency,
                )
        finally:
            loop.close()
    
    def unzip(self, concurrent: int = 5, delete_zipped: bool = False):
        """Unzip all .gz tardis data files in the `temp/zipped/` directory and output to `raw/` directory
        
        Args:
            concurrent (int): number of concurrent unzip operations. Defaults to 5.
            delete_zipped (bool): whether to delete the zipped files after unzipping. Defaults to False.
        """
        src_dir = self.data_dir / "temp/zipped/"
        dst_dir = self.data_dir / "raw/"
        print(f"[{self.__class__.__name__}] Unzipping files from {src_dir} to {dst_dir} with {concurrent} concurrent operations.")
        unzip(src_dir=src_dir, dst_dir=dst_dir, delete_zipped=delete_zipped, concurrent=concurrent)
    
    def _load_api_key_from_env(self) -> str:
        """Load `TARDIS_API_KEY` from project root .env file or environment variables"""
        from .config import tardis_config
        if not tardis_config.api_key:
            raise ValueError(f"TARDIS_API_KEY is not set, please set it in your environment variables or in the .env file, or just pass it to the constructor.")
        return tardis_config.api_key
        
    def _load_data_dir_from_env(self) -> pathlib.Path:
        from .config import tardis_config
        if not tardis_config.data_dir:
            raise ValueError(f"TARDIS_DATA_DIR is not set, please set it in your environment variables or in the .env file, or just pass it to the constructor.")
        return tardis_config.data_dir
        
    def _validate_data_types(self, exchange: Exchange, data_types: list[DataType]):
        if DataType.KLINE in data_types:
            raise ValueError(f"{DataType.KLINE.name} is not a native data type, please remove it when calling TardisRawDownloader.download() method.")
        
        if exchange.name.endswith("SPOT"):
            for data_type in data_types:
                if data_type in [DataType.LIQUIDATIONS, DataType.DERIVATIVE_TICKER]:
                    raise ValueError(f"{data_type.name} is only available for future/option symbols, your exchange is a spot exchange: {exchange.name}")

    def _construct_download_metadatas(self, symbol_idxes: list[int], from_date: datetime.date, to_date: datetime.date, exchange_details: dict):
        symbol_download_metadatas = []
        avail_symbols = exchange_details["availableSymbols"]
        for symbol_idx in symbol_idxes:
            symbol_metadata = avail_symbols[symbol_idx]
            available_since = datetime.fromisoformat(symbol_metadata['availableSince'][:-1]).date()
            if to_date < available_since:
                raise ValueError(f"to_date {to_date} is less than the available_since date {available_since} for symbol {symbol_metadata['id']} in exchange {exchange_details['name']}, please check the available_since date at https://api.tardis.dev/v1/exchanges/{exchange_details['id']}/")
            symbol_metadata['from_date'] = max(available_since, from_date).strftime("%Y-%m-%d")
            symbol_metadata['to_date'] = to_date.strftime("%Y-%m-%d")
            symbol_download_metadatas.append(symbol_metadata)
        return symbol_download_metadatas

    def _check_symbol_existence(self, symbol_list: list[str], exchange_details: dict) -> list[int]:
        symbol_indexes = []
        avail_symbols = exchange_details["availableSymbols"]
        for symbol in symbol_list:
            try:
                symbol_index = next(index for index, d in enumerate(avail_symbols) if d['id'] == symbol)
                symbol_indexes.append(symbol_index)
            except StopIteration:
                raise ValueError(f"Symbol {symbol} is not available for exchange {exchange_details['name']}, please check the available symbols at https://api.tardis.dev/v1/exchanges/{exchange_details['id']}/")
        return symbol_indexes


__all__ = [
    "TardisRawDownloader",
]
