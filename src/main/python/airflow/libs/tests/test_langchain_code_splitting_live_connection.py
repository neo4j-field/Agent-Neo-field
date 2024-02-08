import base64
import json
import unittest
from ..splitter import LangchainCodeSplitter
from ..fetcher import SecretManager
from google.cloud import storage


class TestLangChainSplitting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        env_file_path = ('/Users/alexanderfournier/Downloads/Agent-Neo-field/src/main/python/airflow/tasks/gcpfetch'
                         '/env.json')

        with open(env_file_path, 'r') as f:
            config = json.load(f)

        cls.project_id = config.get('GCP_PROJECT_ID')
        cls.service_account_config = config.get('GOOGLE_SERVICE_ACCOUNT')
        cls.github_access_token = config.get('GITHUB_ACCESS_TOKEN')


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

        bucket_name = sm.access_secret_version('GIT_REPOSITORIES')

        splitter = LangchainCodeSplitter(secret_manager=sm, storage_client=storage_client)

        for doc in splitter.read_from_gcs(bucket_name=bucket_name):
            print(doc)











if __name__ == '__main__':
    unittest.main()
