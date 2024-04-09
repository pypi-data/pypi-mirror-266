import time
import random
import pathlib
import datetime
import traceback
from typing import Union
from itertools import chain
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
from lxml import html
from tqdm import tqdm
from lxml.cssselect import CSSSelector

from finart.yfinance_data.config import finart_yfinance_config
from finart.yfinance_data.utils import yahoo_url_to_article_id
from finart.yfinance_data.crawler.article_crawler import YahooArticleCrawler, YahooArticleParser
from utils import check_or_make_dir, scroll_to_bottom,  SeleniumCrawler, WithLogger, date_from_str, get_headers_and_cookies


class YahooSitemapIndexCrawler(SeleniumCrawler):        
    def crawl(self, start_date: Union[str, datetime.date], end_date: Union[str, datetime.date], n_retries: int = 3) -> None:
        """
        Args:
            start_date (str): start date in the format of '%Y-%m-%d'
            end_date (str): end date in the format of '%Y-%m-%d'
            n_retries (int, optional): number of retries. Defaults to 3.
        """
        # 1. check input validity
        if isinstance(start_date, str):
            start_date = date_from_str(start_date)
        if isinstance(end_date, str):
            end_date = date_from_str(end_date)
        self._ensure_date_validity(start_date, end_date)
        
        self.logger.info(f"Start crawling YahooSitemap from {start_date} to {end_date}...")
        for d in pd.date_range(start_date, end_date):
            n_retry_current = 0
            success = False
            while (not success) and n_retry_current < n_retries:
                try:
                    self._crawl_single_date(d, output_dir=finart_yfinance_config.sitemap_index_html_dir)
                    success = True
                except Exception as e:
                    n_retry_current += 1
                    self.logger.error(f"Failed to crawl YahooSitemap for {d}, retrying {n_retry_current}, error: {e}...")
        self.logger.info(f"Finished crawling YahooSitemap from {start_date} to {end_date}...")
    
    def _ensure_date_validity(self, start_date: datetime.date, end_date: datetime.date):
        """make sure the start_date is no later than end_date, and end_date is no later than today"""
        if end_date > datetime.date.today():
            self.logger.warn(f"[Warning]: end_date {end_date} is later than today, set it to today")
            end_date = datetime.date.today()
        if start_date > end_date:
            raise ValueError("start_date should be no later than end_date")
    
    def _crawl_single_date(self, d: datetime.date, output_dir: pathlib.Path):
        from selenium.webdriver.common.by import By
        
        page_num = 0
        content_selector = "module-sitemapcontent"
        sitemap_url = f'https://finance.yahoo.com/sitemap/{d.strftime("%Y_%m_%d")}/'
        output_dir.mkdir(exist_ok=True)
        self.logger.info(f"[YahooSitemapCrawler] Crawling sitemap for single date: {d}...")
        first_output_path = output_dir / f"{d.strftime('%Y-%m-%d')}_{page_num}.html"
        
        if first_output_path.exists():
            self.logger.info(f"Found at least 1 sitemap html for {d}, at {first_output_path}, skip crawling")
            return

        # 1. 前往 Yahoo Sitemap 网页
        self.driver.get(sitemap_url)
        time.sleep(1.5)
        n_empty_content_max = 5
        n_empty_content = 0
        # 2. 持续爬取, 直到没有下一页或者没有内容
        while True:
            scroll_to_bottom(driver=self.driver, n_scrolls=1, step=2400)
            time.sleep(1.4)
            try:
                self.driver.find_element(By.ID, content_selector)
                output_path = output_dir / f"{d.strftime('%Y-%m-%d')}_{page_num}.html"
                self.logger.info(f"Found sitemap content, saving the page to {output_path}...")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                n_empty_content = 0
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, value="#module-sitemapcontent .sitemapcontent > div:last-child > a:last-child")
                    if next_button.text.strip().lower() == "next":
                        next_button.click()
                        page_num += 1
                    else:
                        self.logger.info(f"next_button.text.strip().lower()=#{next_button.text}# At the end of the sitemap for {d}, current page_num: {page_num}, no next page button found")
                        break
                except Exception as e:
                    self.logger.info(f"At the end of the sitemap for {d}, current page_num: {page_num}, no next page button found")
                    break
            except Exception as e:
                if (n_empty_content < n_empty_content_max):
                    n_empty_content += 1
                    self.logger.info(f"Empty Content for: {d}, error: {e}, page_num: {page_num}, no content found(n_empty_content={n_empty_content}, n_max={n_empty_content_max}), Try refreshing the page...")
                    # refresh the page
                    self.driver.refresh()
                else:
                    if (page_num == 0):
                        self.logger.error(f"Cannot find the a single sitemap at {sitemap_url}, you might be blocked")
                        raise ValueError(f"Cannot find the a single sitemap at {sitemap_url}, you might be blocked")
                    else:
                        self.logger.info(f"(n_refresh full: {n_empty_content}/{n_empty_content_max}) At the end of the sitemap for {d}, page_num: {page_num}, no content found")
                        break


class YahooSitemapIndexParser(WithLogger):
    def parse_one(self, html_path: Union[str, pathlib.Path], output_dir: Union[str, pathlib.Path]) -> None:
        """Parse the sitemap html file, and output the parsed result to `output_dir`(usually one or several csv files)
        
        Args:
            html_path (Union[str, pathlib.Path]): path to the sitemap html file
            output_dir (Union[str, pathlib.Path]): output directory
            
        Raises:
            FileNotFoundError: if the html file not found
            ValueError: if the html file is not a valid html file
            RuntimeError: if cannot parse the html file
        """
        html_path, output_dir = pathlib.Path(html_path), pathlib.Path(output_dir)
        check_or_make_dir(output_dir)
        
        if not html_path.exists():
            raise FileNotFoundError(f"{html_path} not found")
        if not html_path.is_file() or not html_path.suffix == ".html":
            raise ValueError(f"{html_path} is not a valid html file")
        
        try:
            output_index_csv = output_dir / f"{html_path.stem}.csv"
            if output_index_csv.exists():
                return
            tree = html.fromstring(open(html_path, "r", encoding="utf-8").read())
            article_index_dict_list = []
            index_items = CSSSelector("#module-sitemapcontent .sitemapcontent ul>li")(tree)
            date_str = html_path.name.split("_")[0]
            for item in index_items:
                article_url_selector = CSSSelector("a")
                article_url = article_url_selector(item)[0].get("href")
                article_title = article_url_selector(item)[0].text
                publish_date = date_str
                article_index_dict_list.append({
                    "article_url": article_url,
                    "article_title": article_title,
                    "publish_date": publish_date
                })
            df = pd.DataFrame(article_index_dict_list)
            df.to_csv(output_index_csv, index=False)
            
        except Exception as e:
            raise RuntimeError(f"Cannot parse the html file {html_path}") from e

    def parse(self, concurrency: int = 10) -> None:
        """Parse all the sitemap html files in the `finart_yfinance_config.sitemap_html_dir` and output the parsed result to `finart_yfinance_config.sitemap_csv_dir`
        
        Args:
            concurrency (int, optional): number of concurrent parsing processes. Defaults to 10.
        """
        # input validation
        if concurrency <= 0:
            raise ValueError("concurrency should be greater than 0")
        
        html_dir = finart_yfinance_config.sitemap_index_html_dir
        output_dir = finart_yfinance_config.sitemap_index_csv_dir

        htmls = list(html_dir.glob("*.html"))
        need_to_handle_htmls = [h for h in htmls if not (output_dir / f"{h.stem}.csv").exists()]
        if len(need_to_handle_htmls) == 0:
            self.logger.info(f"No sitemap html files need to be parsed")
            return
        self.logger.info(f"Start parsing {len(need_to_handle_htmls)} sitemap html files...")
        concurrency = min(concurrency, len(need_to_handle_htmls))
        with ThreadPoolExecutor(concurrency) as executor:
            list(tqdm(executor.map(lambda h: self.parse_one(h, output_dir), need_to_handle_htmls), total=len(need_to_handle_htmls)))


class YahooSitemapArticleCrawler(WithLogger):
    """Crawl articles from sitemap indexes."""
    def crawl(self, concurrency: int = 6) -> None:
        """Crawl articles from all sitemap indexes with concurrency control.
        
        Args:
            concurrency (int, optional): the number of concurrent threads. Defaults to 6.
        """
        sitemap_csv_dir = finart_yfinance_config.sitemap_index_csv_dir
        sitemap_csv_list = list(sitemap_csv_dir.glob("*.csv"))
        print(f"length of sitemap_csv_list: {len(sitemap_csv_list)}, sitemap_csv_dir: {sitemap_csv_dir}")

        # TODO: manual filtering
        # Step 1: construct date_sitemap_csvs_dict, date can be extracted by `site_csv.stem.split("_")[0]`(e.g. 2023-01-09)
        date_sitemap_csvs_dict = {}
        for sitemap_csv in sitemap_csv_list:
            date_str = sitemap_csv.stem.split("_")[0]
            if date_str not in date_sitemap_csvs_dict:
                date_sitemap_csvs_dict[date_str] = []
            date_sitemap_csvs_dict[date_str].append(sitemap_csv)
        
        # Step 2: for each date, randomly select up to max_csv_per_date(or less) sitemap_csvs, and store them in filtered_sitemap_csvs
        max_csv_per_date = 1000
        filtered_sitemap_csvs = []
        for date_str, sitemap_csvs in date_sitemap_csvs_dict.items():
            if len(sitemap_csvs) <= max_csv_per_date:
                filtered_sitemap_csvs.extend(sitemap_csvs)
            else:
                filtered_sitemap_csvs.extend(random.sample(sitemap_csvs, max_csv_per_date))
        
        # Step 3: concat all sitemap_csvs in filtered_sitemap_csvs, and shuffle them
        random.shuffle(filtered_sitemap_csvs)
        self.logger.info(f"[{self.__class__.__name__}] n_dates: {len(date_sitemap_csvs_dict)}, n_sitemap_csvs: {len(filtered_sitemap_csvs)}, mean: {len(filtered_sitemap_csvs) / len(date_sitemap_csvs_dict):.2f}, std: {np.std([len(v) for v in date_sitemap_csvs_dict.values()]):.2f}, min per day: {min([len(v) for v in date_sitemap_csvs_dict.values()])}, max per day: {max([len(v) for v in date_sitemap_csvs_dict.values()])}")

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_sitemap_csv = {executor.submit(self.crawl_one, sitemap_csv): sitemap_csv for sitemap_csv in filtered_sitemap_csvs}

            for future in as_completed(future_to_sitemap_csv):
                sitemap_csv = future_to_sitemap_csv[future]
                try:
                    future.result()
                except Exception as exc:
                    self.logger.error(f"[{self.__class__.__name__}] Sitemap {sitemap_csv} generated an exception: {exc}, traceback: {traceback.format_exc()}")

        self.logger.info(f"[{self.__class__.__name__}] Finished crawling all articles from sitemap indexes.")
    
    def crawl_one(self, sitemap_csv: pathlib.Path) -> None:
        """Crawl articles from one sitemap index csv file.
        
        Args:
            sitemap_csv (pathlib.Path): the path of the sitemap index csv file
            
        Raises:
            FileNotFoundError: if the sitemap_csv file not found
        """
        if not sitemap_csv.exists():
            raise FileNotFoundError(f"{sitemap_csv} not found")
        
        sitemap_df = pd.read_csv(sitemap_csv)
        if len(sitemap_df) == 0:
            self.logger.info(f"[{self.__class__.__name__}] No articles in {sitemap_csv}")
            return
        
        sitemap_date_str = sitemap_csv.stem.split("/")[-1].split("_")[0]
        output_dir = finart_yfinance_config.sitemap_article_html_dir / sitemap_date_str # store at date-specific folder, e.g. {root_output_dir}/2024-01-06
        check_or_make_dir(output_dir)
        
        sitemap_df['finished'] = sitemap_df['article_url'].apply(lambda x: (output_dir / f"article_{yahoo_url_to_article_id(x)}.html").exists())
        sitemap_df = sitemap_df[~sitemap_df['finished']]
        
        if len(sitemap_df) == 0:
            self.logger.info(f"[{self.__class__.__name__}] All articles in {sitemap_csv} have been crawled.")
            return
        
        crawler = YahooArticleCrawler()
        self.logger.info(f"[{self.__class__.__name__}] Start crawling articles with index data from {sitemap_csv}, prepare cookies and headers...")
        headers, cookies = get_headers_and_cookies()
        self.logger.info(f"[{self.__class__.__name__}] Cookies and headers generated! Start crawling articles with index data from {sitemap_csv}...")
        
        for _, row in tqdm(sitemap_df.iterrows(), total=len(sitemap_df)):
            article_url = row["article_url"]
            if not article_url.startswith("https://finance.yahoo.com"):
                self.logger.warn(f"[{self.__class__.__name__}] Skip non-yahoo article: {article_url}")
                continue
            article_id = yahoo_url_to_article_id(article_url)
            output_path = output_dir / f"article_{article_id}.html"
            if output_path.exists():
                continue
            n_retry_max, n_retry = 2, 0
            while True:
                try:
                    crawler.crawl_by_url(article_url, output_dir=output_dir, headers=headers, cookies=cookies)
                    break
                except Exception as e:
                    self.logger.warn(f"[{self.__class__.__name__}] Error when crawling {article_url}: {e}, n_retry: {n_retry} / {n_retry_max}, traceback: {traceback.format_exc()}")
                    n_retry += 1
                    if n_retry >= n_retry_max:
                        self.logger.error(f"[{self.__class__.__name__}] Skip crawling {article_url} after {n_retry_max} retries.")
                        break
        self.logger.info(f"[{self.__class__.__name__}] Finished crawling articles from {sitemap_csv}")


class YahooSitemapArticleParser(WithLogger):
    def parse_one(self, article_html_path: Union[str, pathlib.Path], output_dir: Union[str, pathlib.Path]) -> None:
        article_html_path, output_dir = pathlib.Path(article_html_path), pathlib.Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        article_parser = YahooArticleParser()
        article_parser.parse_one(article_html_path, output_dir)
    
    def parse(self, concurrency: int = 6) -> None:
        """Parse articles from all sitemap indexes with concurrency control.
        
        Args:
            concurrency (int, optional): the number of concurrent threads. Defaults to 6.
        """
        sitemap_html_dir = finart_yfinance_config.sitemap_article_html_dir
        sitemap_html_date_sub_dirs = list(sitemap_html_dir.glob("*"))
        sitemap_html_list = list(chain(*[list(sub_dir.glob("*.html")) for sub_dir in sitemap_html_date_sub_dirs]))
        sitemap_html_list = [h for h in sitemap_html_list if not (finart_yfinance_config.sitemap_article_json_dir / h.parent.name / f"{h.stem}.json").exists()]
        random.shuffle(sitemap_html_list)

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_sitemap_html = {executor.submit(self.parse_one, sitemap_html, finart_yfinance_config.sitemap_article_json_dir / sitemap_html.parent.name): sitemap_html for sitemap_html in sitemap_html_list}
                    
            for future in tqdm(as_completed(future_to_sitemap_html), total=len(sitemap_html_list), desc="Parsing articles", unit="article"):
                try:
                    future.result()  # 等待任务完成
                except Exception as exc:
                    sitemap_html = future_to_sitemap_html[future]
                    self.logger.error(f"[{self.__class__.__name__}] Sitemap {sitemap_html} generated an exception: {exc}")
                    traceback.print_exc()

        self.logger.info(f"[{self.__class__.__name__}] Finished parsing all articles from sitemap indexes.")


__all__ = [
    'YahooSitemapIndexCrawler',
    'YahooSitemapIndexParser',
    'YahooSitemapArticleCrawler',
    'YahooSitemapArticleParser',
]
