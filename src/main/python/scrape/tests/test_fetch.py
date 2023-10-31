import os
import unittest
from google.cloud import storage
from ..scraper.scrape import Fetcher

class TestFetcher(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        service_account_key = os.getenv('GCP_SERVICE_ACCOUNT_KEY_PATH')
        cls.client = storage.Client.from_service_account_json(service_account_key)
        cls.fetcher = Fetcher(cls.client)

    def test_get_sitemap_urls(self):
        path = os.getenv('GCP_SITEMAPS_BUCKET')
        data = self.fetcher.get_sitemap_urls(path)
        # Check if the returned data is a dictionary and has expected keys or values.
        self.assertIsInstance(data, dict)
        # Add more assertions based on expected content

    def test_get_practitioner_guide_md(self):
        path = os.getenv('GCP_PRACTITIONERS_GUIDE_SITE_BUCKET')
        data = self.fetcher.get_practitioner_guide_md(path)
        self.assertIsInstance(data, dict)
        # Add more assertions based on expected content

    def test_get_other_articles(self):
        path = os.getenv('GCP_SITEMAPS_BUCKET')
        data = self.fetcher.get_other_articles(path)
        self.assertIsInstance(data, dict)
        # Add more assertions based on expected content




if __name__ == '__main__':
    unittest.main()