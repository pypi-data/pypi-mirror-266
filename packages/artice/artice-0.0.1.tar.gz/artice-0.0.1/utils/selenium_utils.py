import time
import logging
from typing import Tuple, Optional

from selenium import webdriver
from utils.log_utils import default_logger


class SeleniumCrawler:
    """selenium-based crawler
    
    It initialized with a Firefox Selenium driver, and a logger.
    """
    from selenium import webdriver
    
    def __init__(self, driver: Optional[webdriver.Firefox] = None, logger: Optional[logging.Logger] = None):
        from selenium import webdriver
        if driver is None:
            option = webdriver.FirefoxOptions()
            option.add_argument("-headless")
            driver = webdriver.Firefox(options=option)
        if logger is None:
            logger = default_logger(__name__)
        self.driver = driver
        self.logger = logger
        

def scroll_to_bottom(driver: webdriver.Firefox, n_scrolls: int = 25, scroll_delay: float = 0.8, step: float = 99999999):
    """Scrolls to the bottom of the page for `n_scrolls` times with a delay of `scroll_delay` seconds

    Args:
        driver (webdriver.Firefox): Selenium Firefox webdriver
        n_scrolls (int, optional): Number of scrolls. Defaults to 25.
        scroll_delay (float, optional): Delay between scrolls. Defaults to 0.8.

    Returns:
        None
    """
    for i in range(n_scrolls):
        time.sleep(scroll_delay)
        driver.execute_script(f"window.scrollTo(0, {step});")


def get_headers_and_cookies(url: str = "https://finance.yahoo.com") -> Tuple[dict[str, str], dict[str, str]]:
    """Generate headers and cookies for a given url.
    
    Args:
        url (str, optional): the url. Defaults to "https://finance.yahoo.com".
        
    Returns:
        Tuple[dict[str, str], dict[str, str]]: headers and cookies
    """
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")  # 无头模式
    options.add_argument("--window-size=1920x1080")

    driver = webdriver.Firefox(options=options)
    driver.get(url)
    cookies = driver.get_cookies()
    cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

    # 注意：除了 User-Agent，其他的 headers 可能需要根据目标网站要求进行定制
    headers = {
        "User-Agent": driver.execute_script("return navigator.userAgent;"),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": url,
    }
    driver.quit()
    return headers, cookies_dict


__all__ = [
    "SeleniumCrawler",
    "scroll_to_bottom",
    "get_headers_and_cookies",
]
