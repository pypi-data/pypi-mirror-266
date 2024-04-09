"""
We crawl finance articles from Yahoo Finance website.

The data is stored at `YFINANCE_ARTICLE_DATA_DIR`, and the directory layout is as follow:

- `indexes/` store the article index data, i.e. the article title, article url and publish_date
- `articles/` store the article data, i.e. the article content crawled from the article url

We have multiple ways to crawl article data, the first way is by sitemaps.
The sitemap crawler stores data at:
- `indexes/sitemap/html/` store the sitemap html files
- `indexes/sitemap/parsed/` store the parsed sitemap data, in the csv format
"""
from .reader import *
from .crawler import *
