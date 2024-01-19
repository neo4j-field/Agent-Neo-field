import unittest
import json
from ..fetcher import SecretManager

#todo: I need to move tests into a better location and fix the relative import of dependencies/modules
class TestSecretManagerReal(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        env_file_path = '/Users/alexanderfournier/Downloads/Agent-Neo-field/src/main/python/airflow/extract/gcp_fetch/env.json'

        # Load data from env.json file
        with open(env_file_path, 'r') as f:
            config = json.load(f)

        cls.gcp_sitemaps_bucket = config.get('GCP_SITEMAPS_BUCKET')
        cls.gcp_practitioners_guide_sites_bucket = config.get('GCP_PRACTITIONERS_GUIDE_SITES_BUCKET')
        cls.gcp_other_articles_bucket = config.get('GCP_OTHER_ARTICLES_BUCKET')
        cls.google_service_account = config.get('GOOGLE_SERVICE_ACCOUNT')
        cls.gcp_processed_docs = config.get('GCP_PROCESSED_DOCS')
        cls.gcp_service_account = config.get('GOOGLE_SERVICE_ACCOUNT')

        # Check if the necessary environment variables are set
        required_vars = [
            cls.gcp_sitemaps_bucket,
            cls.gcp_practitioners_guide_sites_bucket,
            cls.gcp_other_articles_bucket,
            cls.google_service_account,
            cls.gcp_processed_docs,
            cls.gcp_service_account
        ]

        if not all(required_vars):
            raise ValueError("One or more required environment variables are not set.")



    def test_access_secret_version(self):
        # Use a known secret in your GCP project for testing
        secret_id = 'projects/817662103348/secrets/GCP_PROCESSED_DOCS'


        sm = SecretManager(self.gcp_service_account)
        secret = sm.access_secret_version(secret_id)
        print(secret)




if __name__ == '__main__':
    unittest.main()