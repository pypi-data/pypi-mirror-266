import datetime
import unittest
from finart.url_builder.builder import WsjTickerQuoteUrl, WsjIndexQuoteUrl, WsjArchiveUrl


class TestWsjUrlBuilders(unittest.TestCase):

    def test_wsj_ticker_quote_url_parse(self):
        test_urls = [
            ("https://www.wsj.com/market-data/quotes/US/MEDS?mod=md_home_movers_quote", "MEDS", "US"),
            ("https://www.wsj.com/market-data/quotes/AACA", "AACA", None),
            ("https://www.wsj.com/market-data/quotes/AMZN?mod=md_home_movers_quote", "AMZN", None),
        ]
        for url, expected_symbol, expected_country_code in test_urls:
            parsed_url = WsjTickerQuoteUrl.parse(url)
            self.assertEqual(parsed_url.symbol, expected_symbol)
            self.assertEqual(parsed_url.country_code, expected_country_code)

    def test_wsj_index_quote_url_parse(self):
        test_urls = [
            ("https://www.wsj.com/market-data/quotes/index/US/S&P%20US/SPX", "S&P%20US", "US", "SPX"),
            ("https://www.wsj.com/market-data/quotes/index/US/XNAS/COMP", "XNAS", "US", "COMP"),
            ("https://www.wsj.com/market-data/quotes/index/US/DOW%20JONES%20GLOBAL/DJIA", "DOW%20JONES%20GLOBAL", "US", "DJIA"),
            ("https://www.wsj.com/market-data/quotes/index/JP/XTKS/NIK?mod=md_home_overview_quote", "XTKS", "JP", "NIK"),
        ]
        for url, expected_exchange, expected_country_code, expected_index in test_urls:
            parsed_url = WsjIndexQuoteUrl.parse(url)
            self.assertEqual(parsed_url.exchange_code, expected_exchange)
            self.assertEqual(parsed_url.country_code, expected_country_code)
            self.assertEqual(parsed_url.index_code, expected_index)

    def test_wsj_archive_url_parse(self):
        test_urls = [
            ("https://www.wsj.com/news/archive/2023/03/10?page=3", datetime.date(2023, 3, 10), 3),
            ("https://www.wsj.com/news/archive/2023/02/19", datetime.date(2023, 2, 19), None),
        ]

        for url, expected_date, expected_page_num in test_urls:
            parsed_url = WsjArchiveUrl.parse(url=url)
            self.assertEqual(parsed_url.date, expected_date)
            self.assertEqual(parsed_url.page_num, expected_page_num)

    def test_wsj_archive_url_build(self):
        test_dates = [
            (datetime.date(2023, 2, 1), None, "https://www.wsj.com/news/archive/2023/02/01"),
            (datetime.date(2023, 3, 10), 3, "https://www.wsj.com/news/archive/2023/03/10?page=3"),
            (datetime.date(2023, 1, 1), 1, "https://www.wsj.com/news/archive/2023/01/01")
        ]

        for date, page_num, expected_url in test_dates:
            built_url = WsjArchiveUrl.build(date, page_num)
            self.assertEqual(built_url.url, expected_url)


if __name__ == "__main__":
    unittest.main()
