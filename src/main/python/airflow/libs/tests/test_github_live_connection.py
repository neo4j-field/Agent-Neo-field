import unittest
import json
from google.cloud import storage
from ..fetcher import SecretManager, GitHubFetcher
from google.oauth2 import service_account

class TestGitConnectionReal(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        env_file_path = '/Users/alexanderfournier/Downloads/Agent-Neo-field/src/main/python/airflow/tasks/gcpfetch/env.json'

        with open(env_file_path, 'r') as f:
            config = json.load(f)

        cls.gcp_sitemaps_bucket = config.get('GCP_SITEMAPS_BUCKET')
        cls.gcp_practitioners_guide_sites_bucket = config.get('GCP_PRACTITIONERS_GUIDE_SITES_BUCKET')
        cls.gcp_other_articles_bucket = config.get('GCP_OTHER_ARTICLES_BUCKET')
        cls.gcp_processed_docs = config.get('GCP_PROCESSED_DOCS')
        cls.project_id = config.get('GCP_PROJECT_ID')
        cls.service_account_config = config.get('GOOGLE_SERVICE_ACCOUNT')
        cls.github_access_token = config.get('GITHUB_ACCESS_TOKEN')


    def test_git_connection_print_repos(self):


        print(self.service_account_config)

        sm = SecretManager(service_account_info=self.service_account_config,project_id=self.project_id)

        git_fetcher = GitHubFetcher(secret_client=sm)

        repos = git_fetcher.list_github_repos('Neo4j')

        print(repos)


if __name__ == '__main__':
    unittest.main()
