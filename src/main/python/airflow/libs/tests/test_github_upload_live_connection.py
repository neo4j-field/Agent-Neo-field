import unittest
import json
from google.cloud import storage
from ..fetcher import SecretManager, GitHubFetcher
from google.oauth2 import service_account
import base64

class TestGithubUploadReal(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        env_file_path = '/Users/alexanderfournier/Downloads/Agent-Neo-field/src/main/python/airflow/tasks/gcpfetch/env.json'

        with open(env_file_path, 'r') as f:
            config = json.load(f)

        repo_patterns = [
                r'^https://github\.com/neo4j/neo4j\.git$',  # Matches exactly 'https://github.com/neo4j/neo4j.git'
                r'driver',  # Matches any repo with 'driver' in the name
                r'gds',  # Matches any repo with 'gds' in the name
                r'spring',  # Matches any repo with 'spring' in the name
                r'cypher'  # Matches any repo with 'cypher' in the name
            ]

        cls.project_id = config.get('GCP_PROJECT_ID')
        cls.service_account_config = config.get('GOOGLE_SERVICE_ACCOUNT')
        cls.github_access_token = config.get('GITHUB_ACCESS_TOKEN')
        cls.bucket_name = 'agent-neo-github-code'
        cls.repo_patterns = repo_patterns

    @classmethod
    def decode_base64_to_json(cls, base64_str):
        json_bytes = base64.b64decode(base64_str)
        json_str = json_bytes.decode('utf-8')
        data = json.loads(json_str)
        return data

    def test_github_subprocess_write(self):
        service_account_info = self.decode_base64_to_json(self.service_account_config)

        storage_client = storage.Client.from_service_account_info(service_account_info)

        sm = SecretManager(service_account_info=self.service_account_config,project_id=self.project_id)

        git_fetcher = GitHubFetcher(secret_client=sm,storage_client=storage_client)

        repos = git_fetcher.http_get_repos_by_patterns(org_name='Neo4j', repo_patterns=self.repo_patterns)

        for repo in repos:
            git_fetcher.clone_and_upload_repo(repo,self.bucket_name)








if __name__ == '__main__':
    unittest.main()
