from __future__ import annotations

import re
import os
import sys
import pytz
import gzip
import enum
import shutil
import pathlib
import datetime
from typing import Union, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import yfinance as yf
from pydantic import BaseModel, PositiveInt

PathLike = Union[str, pathlib.Path]


def touch_or_make_dir(dir_path: PathLike) -> pathlib.Path:
    """Ensure the dir_path is a directory, if not exist, create it."""
    dir_path = pathlib.Path(dir_path)
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
    else:
        if not dir_path.is_dir():
            raise ValueError(f"{dir_path} is not a directory")
    return dir_path


def unzip_file(src_path: str, dst_path: str, delete_gz: bool = False) -> None:
    """Helper function to unzip a single file.
    
    Args:
        src_path (str): The source path of the .gz file to unzip.
        dst_path (str): The destination path to save the unzipped file.
        delete_gz (bool): Whether to delete the .gz file after unzipping.
    """
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    if not os.path.exists(dst_path):
        with gzip.open(src_path, "rb") as f_in:
            with open(dst_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
    if delete_gz and os.path.exists(src_path):
        os.remove(src_path)


def unzip(src_dir: str, dst_dir: str, concurrent: int = 5, delete_zipped: bool = False):
    """Unzip all .gz files in the base directory concurrently.
    
    Args:
        base_dir (str): The base directory from which to unzip files.
        concurrent (int): The number of concurrent unzip operations.
    """
    files_to_unzip = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".gz"):
                src_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(src_file_path, src_dir)
                dst_file_path = os.path.join(dst_dir, relative_path[:-3])
                files_to_unzip.append((src_file_path, dst_file_path))

    files_to_unzip = sorted(files_to_unzip)
    if len(files_to_unzip) == 0:
        print(f"No .gz files found in {src_dir} and its subdirectories.")
        return

    concurrent = min(concurrent, len(files_to_unzip))
    futures = []
    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = [executor.submit(unzip_file, src_path, dst_path, delete_zipped) for src_path, dst_path in files_to_unzip]

        for _ in as_completed(futures):
            pass


def get_today_str() -> str:
    """Return the current date in string format."""
    return datetime.datetime.now().strftime("%Y-%m-%d")


class KlineInterval(enum.IntEnum):
    SECOND = 1
    SECOND_3 = 3
    SECOND_5 = 5
    SECOND_10 = 10
    SECOND_15 = 15
    MINUTE = 60
    MINUTE_3 = 180
    MINUTE_5 = 300
    MINUTE_10 = 600
    MINUTE_15 = 900
    HOUR = 3600
    HOUR_4 = 14400
    HOUR_6 = 21600
    HOUR_8 = 28800
    HOUR_12 = 43200
    DAY = 86400
    WEEK = 604800
    MONTH = 2592000
    YEAR = 31536000
    
    @classmethod
    def parse(cls, str) -> KlineInterval:
        m = re.match(r"(\d+)([smhdwMy])", str)
        flag_dict = {
            "s": 1,
            "m": 60,
            "h": 3600,
            "d": 86400,
            "w": 604800,
            "M": 2592000,
            "y": 31536000,
        }
        if m:
            num, unit = m.groups()
            return cls(int(num) * flag_dict[unit])
        else:
            raise ValueError(f"Invalid KlineInterval string: {str}, it should be like '1m', '3h', '1d', etc.")


class Period(BaseModel):
    name: str
    """the string representation of the period"""
    value: PositiveInt
    """total seconds of the period"""
    
    @classmethod
    def parse(cls, period: str) -> Period:
        """time unit can be 's', 'm', 'h', 'd', 'w', 'M', 'y', and a special one: 'max'(it should be the largest integer)"""
        if period == 'max':
            return cls(value=sys.maxsize, name='max')
        m = re.match(r"(\d+)([smhdwMy])", period)
        if m:
            num, unit = m.groups()
            flag_dict = {
                "s": 1,
                "m": 60,
                "h": 3600,
                "d": 86400,
                "w": 604800,
                "M": 2592000,
                "y": 31536000,
            }
            return cls(value=int(num) * flag_dict[unit], name=period)
        else:
            raise ValueError(f"Invalid period string: {period}, it should be like '1m', '3h', '1d', etc.")

    def to_yfinance_repr(self) -> str:
        """Compatible with yfinance representation
        
        We use 'M' for month, while yfinance uses 'mo'.
        """
        if self.name.endswith("M"):
            return f"{self.value // 2592000}mo"
        else:
            return self.name
        
    # overwrite the compare method
    def __eq__(self, other: Period) -> bool:
        return self.value == other.value
    
    def __lt__(self, other: Period) -> bool:
        return self.value < other.value
    
    def __le__(self, other: Period) -> bool:
        return self.value <= other.value
    
    def __gt__(self, other: Period) -> bool:
        return self.value > other.value
    
    def __ge__(self, other: Period) -> bool:
        return self.value >= other.value


def read_daily_kline_yfinance(csv_path: PathLike) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df['Date'] = df['Date'].apply(lambda x: datetime.datetime.strptime(x.split()[0], "%Y-%m-%d"))
    return df


def yf_download(ticker: str, period: str = 'max', start: Optional[str] = None, end: Optional[str] = None, interval: str = '1d', timezone = pytz.timezone("America/New_York")) -> pd.DataFrame:
    """Download data from Yahoo Finance using yfinance library.
    
    Args:
        ticker (str): The ticker of the stock.
        period (str): The period of the data, e.g., '1d', '1m', '1y', 'max'. Default is 'max'
        start (str): The start date of the data in string format, e.g., '2021-01-01'. Default is '1930-01-01'. This will expire in 2030-01-01 since daily data is only available for the last 100 years.
        end (str): The end date of the data in string format, e.g., '2021-12-31'. Default is today.
        interval (str): The interval of the data, e.g., '1m', '1h', '1d'. Default is '1d'.
        timezone (pytz.timezone): The timezone to localize the start and end date.
        
    Returns:
        pd.DataFrame: The downloaded data.
    """
    if end is None:
        end = get_today_str()
    
    df = yf.download(
        tickers=[ticker], 
        start=start, 
        end=end,
        auto_adjust=True,
        interval=interval,
        period=period,
        progress=False,
    )
    return df
