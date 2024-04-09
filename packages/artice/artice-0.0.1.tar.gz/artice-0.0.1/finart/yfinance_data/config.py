import os
import pathlib

from utils import check_or_make_dir


class FinartYfinanceConfig:
    def __init__(self):
        self.data_dir = self._load_finart_dir() / "yfinance-data"
        check_or_make_dir(self.data_dir)
        
        self.article_html_dir = self.data_dir / "articles/html"
        
        self.sitemap_index_html_dir = self.data_dir / "indexes/sitemap/html"
        self.sitemap_index_csv_dir = self.data_dir / "indexes/sitemap/parsed"
        self.sitemap_article_html_dir = self.data_dir / "articles/sitemap/html"
        self.sitemap_article_json_dir = self.data_dir / "articles/sitemap/parsed"

        check_or_make_dir(self.sitemap_index_html_dir)
        check_or_make_dir(self.sitemap_index_csv_dir)
        check_or_make_dir(self.sitemap_article_html_dir)
        check_or_make_dir(self.sitemap_article_json_dir)
        
    def _load_finart_dir(self) -> pathlib.Path:
        from dotenv import load_dotenv

        load_dotenv()
        finart_dir = os.getenv("FINART_DATA_DIR")
        if not finart_dir:
            finart_dir = self._default_finart_dir()
        return pathlib.Path(finart_dir)
    
    def _default_finart_dir(self) -> pathlib.Path:
        username = os.getenv("USERNAME")
        if os.name == "nt":
            p = pathlib.Path(f"C:/Users/{username}/.finart")
        else:
            p = pathlib.Path(f"/home/{username}/.finart")
        return p
        
        
finart_yfinance_config = FinartYfinanceConfig()


__all__ = [
    "FinartYfinanceConfig",
    "finart_yfinance_config",
]
