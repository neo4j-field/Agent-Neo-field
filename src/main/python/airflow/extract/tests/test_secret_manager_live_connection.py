import unittest
import json
import base64
import os
from ..fetcher import SecretManager


class TestSecretManagerReal(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        env_file_path = '/Users/alexanderfournier/Downloads/Agent-Neo-field/src/main/python/airflow/extract/gcpfetch/env.json'

        with open(env_file_path, 'r') as f:
            config = json.load(f)

        cls.gcp_sitemaps_bucket = config.get('GCP_SITEMAPS_BUCKET')
        cls.gcp_practitioners_guide_sites_bucket = config.get('GCP_PRACTITIONERS_GUIDE_SITES_BUCKET')
        cls.gcp_other_articles_bucket = config.get('GCP_OTHER_ARTICLES_BUCKET')
        cls.gcp_processed_docs = config.get('GCP_PROCESSED_DOCS')
        cls.project_id = config.get('GCP_PROJECT_ID')
        cls.service_account_config = config.get('GOOGLE_SERVICE_ACCOUNT')


        required_vars = [
            cls.gcp_sitemaps_bucket,
            cls.gcp_practitioners_guide_sites_bucket,
            cls.gcp_other_articles_bucket,
            cls.gcp_processed_docs,
            cls.project_id,
            cls.service_account_config
        ]

        if not all(required_vars):
            raise ValueError("One or more required environment variables are not set.")

    def test_access_secret_version(self):
        secret_id = 'GCP_OTHER_ARTICLES_BUCKET'

        sm = SecretManager(service_account_info=self.service_account_config,project_id=self.project_id)
        secret = sm.access_secret_version(secret_id)
        print(secret)

if __name__ == '__main__':
    unittest.main()
