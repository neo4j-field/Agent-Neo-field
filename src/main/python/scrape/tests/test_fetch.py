import os
import unittest
from google.cloud import storage
from scrape.scraper.scrape import Fetcher  # Ensure you've imported Fetcher from wherever it's defined

class TestFetcher(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = storage.Client()
        # Initialize the Fetcher with the GCP client
        cls.fetcher = Fetcher(cls.client)

    def test_get_sitemap_urls(self):
        data = self.fetcher.get_sitemap_urls()
        # Check if the returned data is a dictionary and has expected keys or values.
        self.assertIsInstance(data, dict)
        # Add more assertions based on expected content

    def test_get_practitioner_guide_md(self):
        data = self.fetcher.get_practitioner_guide_md()
        self.assertIsInstance(data, dict)
        # Add more assertions based on expected content

    def test_get_other_articles(self):
        data = self.fetcher.get_other_articles()
        self.assertIsInstance(data, dict)
        # Add more assertions based on expected content

    def test_concatenate_unique_ordered(self):
        result = self.fetcher.concatenate_unique_ordered([1, 2, 3], [3, 4, 5], [5, 6])
        self.assertEqual(result, [1, 2, 3, 4, 5, 6])

if __name__ == '__main__':
    unittest.main()