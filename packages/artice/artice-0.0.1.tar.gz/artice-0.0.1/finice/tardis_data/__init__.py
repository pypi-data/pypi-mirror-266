"""
[Tardis](https://tardis.dev) provide tick-level granual data for Crypto Market. You need a **Tardis API Key** to access the data.

Tardis data directory contains the following subdirectories:
- `temp/zipped/`: Contains the raw zipped data files
- `temp/intermediate/`: Contains the intermediate data files, such as cache during synthesizing klines, this folder should always be empty after synthesizing 
- `raw/`: Contains the row data files(unzipped from `temp/zipped/`)
- `kline/`: Contains the second-level kline data files
- `orderbook/`: Contains the reconstructed tick-level orderbook data files

All data files are stored in `csv` format
"""
from .raw import TardisRawDownloader
from .utils import Exchange, DataType
from .kline import TardisKlineSynthesizer, TardisKlineReader, KlineInterval

__all__ = [
    'Exchange',
    'DataType',
    'KlineInterval',
    'TardisRawDownloader',
    'TardisKlineReader',
    'TardisKlineSynthesizer',
]
