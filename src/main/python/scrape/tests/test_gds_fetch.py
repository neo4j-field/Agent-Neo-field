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

    @unittest.skip("")
    def test_get_urls(self):
        token = os.getenv('GITHUB_TOKEN')
        list_of_urls = self.fetcher._list_github_repos(org_name='neo4j')
        print(list_of_urls)



    def test_get_filtered_urls(self):
        filtered_list = self.fetcher.get_repos_by_pattern(org_name='neo4j',pattern='graph-data-science-client')
        print(filtered_list)



