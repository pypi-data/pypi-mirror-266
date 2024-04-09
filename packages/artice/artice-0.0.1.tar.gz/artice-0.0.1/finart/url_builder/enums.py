from __future__ import annotations

from enum import Enum

WSJ_BASE_URL = "https://www.wsj.com"


class WsjArticleCategory(str, Enum):
    World = "world"


class WsjDomain(str, Enum):
    MarketData = "market-data"
    Search = "search"
    News = "news"
    USNews = "us-news"
    Bussiness = "business"
    Tech = "tech"
    Politics = "politics"
    Finance = "finance"
    ArtCulture = "arts-culture"
    RealEstate = "real-estate"

    @classmethod
    def list_all(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def from_value(cls, value: str) -> WsjDomain:
        for domain in cls:
            if domain.value == value:
                return domain
        raise ValueError(f"Invalid domain: {value}, valid values are: {cls.list_all()}")
