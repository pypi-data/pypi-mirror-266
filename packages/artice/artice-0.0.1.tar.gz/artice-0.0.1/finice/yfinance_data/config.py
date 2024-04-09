import os
import pathlib

from utils import check_or_make_dir


class FiniceYfinanceConfig:
    api_key = None

    def __init__(self):
        self.data_dir = self._load_finice_dir() / "yfinance-data"
        check_or_make_dir(self.data_dir)
        
    def _load_finice_dir(self) -> pathlib.Path:
        from dotenv import load_dotenv

        load_dotenv()
        finice_dir = os.getenv("FINICE_DATA_DIR")
        if not finice_dir:
            finice_dir = self._default_finice_dir()
        return pathlib.Path(finice_dir)
    
    def _default_finice_dir(self) -> pathlib.Path:
        username = os.getenv("USERNAME")
        if os.name == "nt":
            p = pathlib.Path(f"C:/Users/{username}/.finice")
        else:
            p = pathlib.Path(f"/home/{username}/.finice")
        return p


finice_yfinance_config = FiniceYfinanceConfig()
"""Global configuration for the yfinance_data package."""


__all__ = [
    'FiniceYfinanceConfig',
    'finice_yfinance_config',
]
