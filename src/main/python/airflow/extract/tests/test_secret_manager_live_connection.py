import unittest
import json
import base64
import os
from ..fetcher import SecretManager


class TestSecretManagerReal(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        env_file_path = '/Users/alexanderfournier/Downloads/Agent-Neo-field/src/main/python/airflow/extract/gcp_fetch/env.json'

        with open(env_file_path, 'r') as f:
            config = json.load(f)

        cls.gcp_sitemaps_bucket = config.get('GCP_SITEMAPS_BUCKET')
        cls.gcp_practitioners_guide_sites_bucket = config.get('GCP_PRACTITIONERS_GUIDE_SITES_BUCKET')
        cls.gcp_other_articles_bucket = config.get('GCP_OTHER_ARTICLES_BUCKET')
        cls.gcp_processed_docs = config.get('GCP_PROCESSED_DOCS')
        cls.project_id = config.get('GCP_PROJECT_ID')

        service_account_info = base64.b64decode(config.get('GOOGLE_SERVICE_ACCOUNT')).decode('utf-8')
        cls.service_account_dict = json.loads(service_account_info)

        required_vars = [
            cls.gcp_sitemaps_bucket,
            cls.gcp_practitioners_guide_sites_bucket,
            cls.gcp_other_articles_bucket,
            cls.service_account_dict,
            cls.gcp_processed_docs,
            cls.project_id
        ]

        if not all(required_vars):
            raise ValueError("One or more required environment variables are not set.")

    def test_access_secret_version(self):
        secret_id = 'projects/817662103348/secrets/GCP_PROCESSED_DOCS'

        sm = SecretManager(service_account_info=self.service_account_dict,project_id=self.project_id)
        secret = sm.access_secret_version(secret_id)
        print(secret)

if __name__ == '__main__':
    unittest.main()
