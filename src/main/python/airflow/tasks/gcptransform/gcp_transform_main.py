from google.cloud import storage
from google.oauth2 import service_account
from libs.fetcher.secret_manager import SecretManager
from libs.fetcher.gcp_fetcher import GCPFetcher






if __name__ == '__main__':
    secret_manager = SecretManager(project_id='neo4j-cs-team-201901')

    service_account_info = secret_manager.access_secret_version('GCP_SERVICE_ACCOUNT')

    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    gcp_client = storage.Client(credentials=credentials)






