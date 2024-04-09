import pathlib
from typing import Union, Optional

import json
import requests
from lxml import html

from utils import WithLogger, check_or_make_dir, get_headers_and_cookies
from finart.yfinance_data.utils import yahoo_url_to_article_id, article_id_to_yahoo_url


class YahooArticleCrawler(WithLogger):
    """General Yahoo Finance Article Crawler."""
    # FIXME: article_url can be external link, e.g. https://www.telegraph.co.uk/business/2023/11/01/ftse-100-market-news-ai-summit-house-prices-fed-rate-latest/
    def crawl_by_url(self, article_url: str, output_dir: Union[str, pathlib.Path], headers: Optional[str] = None, cookies: Optional[str] = None) -> pathlib.Path:
        """
        Args:
            article_url: str, e.g. https://finance.yahoo.com/news/tonkens-agrar-ags-etr-gtk-062854653.html, or https://www.telegraph.co.uk/business/2023/11/01/ftse-100-market-news-ai-summit-house-prices-fed-rate-latest/
            output_dir: Union[str, pathlib.Path], the path of the output directory
            headers: Optional[str], the headers for the request, if None, will generate a new one. Strongly recommend to provide the headeres for efficient crawling!
            cookies: Optional[str], the cookies for the request, if None, will generate a new one. Strongly recommend to provide the cookies for efficient crawling!
            
        Returns:
            pathlib.Path: the path of the saved html file
        """
        # 1. input validation
        output_dir = pathlib.Path(output_dir)
        if headers is None or cookies is None:
            n_retry, retry = 0, 3
            while True:
                try:
                    headers, cookies = get_headers_and_cookies()
                    break
                except Exception as e:
                    self.logger.warn(f"Failed to get headers and cookies before crawling {article_url}, retrying...({n_retry}/{retry})")
                    n_retry += 1
                    if n_retry >= retry:
                        raise RuntimeError(f"Cannot get headers and cookies, error: {e}")

        # 2. crawl the article
        selector = "#module-article article"
        response = requests.get(article_url, headers=headers, cookies=cookies)
        tree = html.fromstring(response.text)
        try:
            article = tree.cssselect(selector)[0]
            article_html = html.tostring(article).decode("utf-8")
            article_id = yahoo_url_to_article_id(article_url)
            with open(output_dir / f"article_{article_id}.html", "w", encoding="utf-8") as f:
                f.write(article_html)
        except IndexError:
            raise ValueError(f"Cannot find article in {article_url} with current request, please retry or check the url: {article_url} and selector: {selector}")
    
    def crawl_by_id(self, article_id: str, output_dir: Union[str, pathlib.Path]) -> pathlib.Path:
        """Crawl article by article_id.
        
        Args:
            article_id (str): the article id, e.g. "news_tonkens-agrar-ags-etr-gtk-062854653"
            output_dir (Union[str, pathlib.Path]): the path of the output directory
        """
        url = article_id_to_yahoo_url(article_id)
        return self.crawl_by_url(url, output_dir)


class YahooArticleParser(WithLogger):
    def parse_one(self, article_html_path: Union[str, pathlib.Path], output_dir: Union[str, pathlib.Path]) -> None:
        """Parse one article html file.
        
        Args:
            article_html_path (Union[str, pathlib.Path]): the path of the article html file
            output_dir (Union[str, pathlib.Path]): the output directory
        """
        article_html_path, output_dir = pathlib.Path(article_html_path), pathlib.Path(output_dir)
        if not article_html_path.exists():
            raise FileNotFoundError(f"{article_html_path} not found")
        check_or_make_dir(output_dir)
        article_id = article_html_path.stem
            
        output_path = output_dir / f"{article_id}.json"
        if output_path.exists():
            return
        
        try:
            tree = html.fromstring(open(article_html_path, "r", encoding="utf-8").read())
            article_title = tree.cssselect(".caas-title-wrapper > h1")[0].text_content()
            article_content = tree.cssselect(".caas-body")[0].text_content()
            article_author = tree.cssselect(".caas-attr-item-author")[0].text_content()
            article_provider = tree.cssselect(".caas-attr-provider")[0].text_content()
            publish_time = tree.cssselect(".caas-attr-time-style > time")[0].get("datetime")
            finticker_names = [finticker.get("symbol") for finticker in tree.cssselect("fin-ticker")] # fintickers are tickers related to the article, tagged by <fin-ticker> elements. Earlier articles, say articles in 2018 have no fintickers.
            links_in_articles = [link.get("href") for link in tree.xpath("//a")]
            fin_related_quotes = [quote.get('data-symbol') for quote in tree.cssselect("table.related-quotes-table td.data-col1 > fin-streamer")]
            finticker_names = list(set(finticker_names + fin_related_quotes))
            
            article_dict = {
                "id": article_id,
                "url": article_id_to_yahoo_url(article_id),
                "title": article_title,
                "publish_time": publish_time,
                "author": article_author,
                "provider": article_provider,
                "content": article_content,
                "fin_tickers": finticker_names,
                "in_article_links": links_in_articles,
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(article_dict, f)
        except Exception as e:
            raise RuntimeError(f"Failed to parse the html file {article_html_path}") from e
       

__all__ = [
    "YahooArticleCrawler",
    "YahooArticleParser",
]
