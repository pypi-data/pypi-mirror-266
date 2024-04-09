from __future__ import annotations

import re
import abc
import datetime
from typing import Optional
from urllib.parse import quote, unquote

from finart.url_builder.enums import WSJ_BASE_URL, WsjDomain


class Url(abc.ABC):
    """Url Util class

    Always use `build` and `parse` to create and parse urls, respectively.
    Don't use `__init__` directly.
    """

    def __init__(self):
        self.url = None
        """the actual url string"""

    @abc.abstractclassmethod
    def build(cls, **kwargs) -> Url:
        pass

    @abc.abstractclassmethod
    def parse(cls, url: str) -> Url:
        pass

    def __str__(self) -> str:
        return self.url

    def __repr__(self) -> str:
        return self.__str__()


class WsjTickerQuoteUrl(Url):
    """Ticker Quote Url, usually contain the quote market data, and may contain some related news, statements, etc...

    Example:
    - https://www.wsj.com/market-data/quotes/US/MEDS?mod=md_home_movers_quote
    - https://www.wsj.com/market-data/quotes/AACA
    - https://www.wsj.com/market-data/quotes/AMZN?mod=md_home_movers_quote
    """

    url_re = re.compile(
        rf"{WSJ_BASE_URL}/{WsjDomain.MarketData.value}/quotes/(?P<country_code>\w+/)?(?P<symbol>[^?/]+)"
    )

    def __init__(
        self, symbol: str, country_code: Optional[str] = None, url: Optional[str] = None
    ):
        super().__init__()
        if country_code == "index":
            raise ValueError(
                f"Invalid country code: {country_code}, this might be an index quote url"
            )
        self.symbol = unquote(symbol)
        """the ticker symbol, compatiable with the symbol defined on http://www.wsj.com"""
        self.country_code = country_code
        """the country code, compatiable with the abbr on http://www.wsj.com"""
        country_str = f"{quote(country_code)}/" if country_code else ""
        symbol_quoted = quote(symbol)
        if url:
            self.url = url
        else:
            self.url = f"{WSJ_BASE_URL}/{WsjDomain.MarketData.value}/quotes/{country_str}{symbol_quoted}"

    @classmethod
    def build(
        cls, symbol: str, country_code: Optional[str] = None
    ) -> WsjTickerQuoteUrl:
        return WsjTickerQuoteUrl(symbol, country_code)

    @classmethod
    def parse(cls, url: str) -> WsjTickerQuoteUrl:
        match = cls.url_re.match(url)
        if not match:
            raise ValueError(
                f"Invalid {cls.__name__} url: {url}, expected format: {cls.url_re.pattern}"
            )
        symbol = unquote(match.group("symbol")).strip("/")
        country_code = (
            unquote(match.group("country_code")).strip("/")
            if match.group("country_code")
            else None
        )
        return WsjTickerQuoteUrl(symbol, country_code, url=url)


class WsjIndexQuoteUrl(Url):
    """Index Quote Url, usually contain the market index data, and related news, remarks, etc...

    Example:
    - https://www.wsj.com/market-data/quotes/index/US/S&P%20US/SPX
    - https://www.wsj.com/market-data/quotes/index/US/XNAS/COMP
    - https://www.wsj.com/market-data/quotes/index/US/DOW%20JONES%20GLOBAL/DJIA
    - https://www.wsj.com/market-data/quotes/index/JP/XTKS/NIK?mod=md_home_overview_quote
    """

    url_re = re.compile(
        rf"{WSJ_BASE_URL}/{WsjDomain.MarketData.value}/quotes/index/(?P<country_code>\w+)/(?P<exchange_code>[^?/]+)/(?P<index_code>[^?/]+)"
    )

    def __init__(
        self,
        country_code: str,
        exchange_code: str,
        index: str,
        url: Optional[str] = None,
    ):
        super().__init__()
        self.country_code = country_code
        """Country code, compatible with the codes defined on http://www.wsj.com, e.g. US, JP"""
        self.exchange_code = exchange_code
        """Exchange code, compatible with the codes defined on http://www.wsj.com, e.g. XNAS, XTKS"""
        self.index_code = unquote(index)
        """Index identifier, compatible with the index names defined on http://www.wsj.com, e.g. NIK, DOW, COMP, SPX"""
        if url:
            self.url = url
        else:
            self.url = f"{WSJ_BASE_URL}/{WsjDomain.MarketData.value}/quotes/index/{country_code}/{exchange_code}/{quote(index)}"

    @classmethod
    def build(
        cls, country_code: str, exchange_code: str, index_code: str
    ) -> WsjIndexQuoteUrl:
        return WsjIndexQuoteUrl(country_code, exchange_code, index_code)

    @classmethod
    def parse(cls, url: str) -> WsjIndexQuoteUrl:
        match = cls.url_re.match(url)
        if not match:
            raise ValueError(
                f"Invalid {cls.__name__} url: {url}, expected format: {cls.url_re.pattern}"
            )
        country_code = match.group("country_code")
        exchange_code = match.group("exchange_code")
        index_code = unquote(match.group("index_code"))
        return WsjIndexQuoteUrl(country_code, exchange_code, index_code, url=url)


class WsjArchiveUrl(Url):
    """Wsj Archive Url, contains the article list of the specified date...

    Example:
    - https://www.wsj.com/news/archive/2023/03/10?page=3
    - https://www.wsj.com/news/archive/2023/02/19
    """

    url_re = re.compile(
        rf"{WSJ_BASE_URL}/{WsjDomain.News.value}/archive/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)(\?page=(?P<page_num>\d+))?"
    )

    def __init__(
        self,
        date: datetime.date,
        page_num: Optional[int] = None,
        url: Optional[str] = None,
    ):
        super().__init__()
        self.date = date
        self.page_num = page_num
        if url:
            self.url = url
        else:
            self.url = (
                f"{WSJ_BASE_URL}/{WsjDomain.News.value}/archive/{date.year}/{date.month:02d}/{date.day:02d}"
                + (f"?page={page_num}" if page_num and page_num > 1 else "")
            )

    @classmethod
    def build(
        cls, date: datetime.date, page_num: Optional[int] = None
    ) -> WsjArchiveUrl:
        return WsjArchiveUrl(date, page_num)

    @classmethod
    def parse(cls, url: str) -> WsjArchiveUrl:
        match = cls.url_re.match(url)
        if not match:
            raise ValueError(
                f"Invalid {cls.__name__} url: {url}, expected format: {cls.url_re.pattern}"
            )
        year = int(match.group("year"))
        month = int(match.group("month"))
        day = int(match.group("day"))
        page_num = int(match.group("page_num")) if match.group("page_num") else None
        return WsjArchiveUrl(datetime.date(year, month, day), page_num, url=url)


__all__ = [
    "Url",
    "WsjArchiveUrl",
    "WsjIndexQuoteUrl",
    "WsjTickerQuoteUrl",
]
