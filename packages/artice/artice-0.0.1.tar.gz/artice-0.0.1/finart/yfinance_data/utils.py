import json
import pathlib
import datetime
from typing import Union


def yahoo_url_to_article_id(url: str) -> str:
    prefix = "https://finance.yahoo.com/"
    if url.startswith(prefix):
        article_id = url[len(prefix):]  # 使用切片移除URL前缀
    else:
        article_id = url
    article_id = article_id.rstrip(".html").replace("/", "_")
    return article_id


def article_id_to_yahoo_url(article_id: str) -> str:
    url_path = article_id.replace('_', '/')
    return f"https://finance.yahoo.com/{url_path}.html"


def read_article_json(json_path: Union[str, pathlib.Path]) -> dict:
    with open(json_path, 'r', encoding='utf-8') as file:
        article_dict = json.load(file)
    
    article_dict['publish_time'] = datetime.datetime.strptime(
        article_dict['publish_time'], '%Y-%m-%dT%H:%M:%S.%fZ'
    ).replace(tzinfo=datetime.timezone.utc)
    
    if 'id' in article_dict:
        article_dict['article_id'] = article_dict.pop('id')
    article_dict['non_empty_fin_tickers'] = len(article_dict['fin_tickers']) > 0

    return article_dict
