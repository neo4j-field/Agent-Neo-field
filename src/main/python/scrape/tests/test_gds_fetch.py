import os
import unittest
from google.cloud import storage
from ..scraper.scrape import Fetcher
import requests


class TestFetcher(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        service_account_key = os.getenv('GCP_SERVICE_ACCOUNT_KEY_PATH')
        cls.client = storage.Client.from_service_account_json(service_account_key)
        cls.token = os.getenv('GITHUB_TOKEN')
        cls.fetcher = Fetcher(cls.client, cls.token)

    @unittest.skip("")
    def test_get_urls(self):
        list_of_urls = self.fetcher._list_github_repos(org_name='neo4j')
        print(list_of_urls)

    @unittest.skip("")
    def test_get_filtered_urls(self):
        filtered_list = self.fetcher.get_repos_by_pattern(org_name='neo4j', pattern='graph-data-science-client')
        print(filtered_list)

    def test_fetch_files_from_git_repos(self):
        org_name = 'neo4j'
        repo_pattern = 'graph-data-science-client'

        file_contents = self.fetcher.fetch_files_from_git_repos(org_name=org_name, repo_pattern=repo_pattern)

        for file_path, file_data in file_contents.items():
            print(f"File Path: {file_path}")
            print("File Content:")
            print(file_data)

    def test_get_rate_limits(self):
        url = "https://api.github.com/rate_limit"
        response = requests.get(url, headers={'Authorization': f'token {self.token}'})
        if response.status_code == 200:
            rate_limit_info = response.json()
            print("Rate Limit Status:")
            print(rate_limit_info)
        else:
            print("Failed to retrieve rate limit information. Status Code:", response.status_code)


if __name__ == '__main__':
    unittest.main()
