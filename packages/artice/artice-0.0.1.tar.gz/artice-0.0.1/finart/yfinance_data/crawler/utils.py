def parse_article_card(element) -> dict:
    """Parse an article card from the market stock news page."""
    # 检查是否为广告, 如果有"Ad"标记，跳过广告
    if element.xpath('.//div[@data-test-locator="react-gemini-feedback-container"]'):
        return None
    # 检查是否是视频
    # if element.xpath('.//div[@data-test-locator="mega"]'):
        # return None
    data = {}
    try:
        data["title"] = element.xpath(".//h3/a/text()")[0]
    except IndexError:
        pass
    try:
        data["link"] = element.xpath(".//h3/a/@href")[0]
        if data["link"].startswith("/"):
            data["link"] = "https://finance.yahoo.com" + data["link"]
    except IndexError:
        pass
    try:
        data["summary"] = element.xpath(".//p/text()")[0]
    except IndexError:
        pass
    try:
        data["category"] = element.xpath('.//div[@data-test-locator="catlabel"]/text()')[0]
    except IndexError:
        pass
    try:
        data["source"] = element.xpath('.//div[@class="C(#959595) Fz(11px) D(ib) Mb(6px)"]/span/text()')[0]
    except IndexError:
        pass
    try:
        data["time_str"] = element.xpath('.//div[@class="C(#959595) Fz(11px) D(ib) Mb(6px)"]/span[2]/text()')[0]
    except IndexError:
        pass
    try:
        srcset_value = element.xpath('.//div[@class="H(0) Ov(h) Bdrs(2px)"]/img/@srcset')[0]
        data["avatar_url"] = srcset_value.split(",")[-1].split()[0]
        if data["avatar_url"].startswith("/"):
            data["avatar_url"] = "https://finance.yahoo.com" + data["avatar_url"]
    except IndexError:
        pass

    return data


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
