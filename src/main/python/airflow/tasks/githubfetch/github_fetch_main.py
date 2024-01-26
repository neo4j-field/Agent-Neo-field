from google.cloud import storage
from google.oauth2 import service_account
from src.main.python.airflow.libs import SecretManager
from src.main.python.airflow.libs import GitHubFetcher

#todo fix the relative imorts somehow with __init__.py
if __name__ == '__main__':
    secret_manager = SecretManager(project_id='neo4j-cs-team-201901')

    service_account_info = secret_manager.access_secret_version('GCP_SERVICE_ACCOUNT')

    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    gcp_client = storage.Client(credentials=credentials)


    git_fetcher = GitHubFetcher(storage_client=gcp_client, secret_client=secret_manager)

    repos = git_fetcher.list_github_repos()

    print(repos)
