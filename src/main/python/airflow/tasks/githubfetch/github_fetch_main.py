from google.cloud import storage
from libs.fetcher.secret_manager import SecretManager
from libs.fetcher.github_fetcher import GitHubFetcher

#todo fix the relative imorts somehow with __init__.py
if __name__ == '__main__':

    repo_patterns = [
        r'^https://github\.com/neo4j/neo4j\.git$',  # Matches exactly 'https://github.com/neo4j/neo4j.git'
        r'driver',  # Matches any repo with 'driver' in the name
        r'gds',  # Matches any repo with 'gds' in the name
        r'spring',  # Matches any repo with 'spring' in the name
        r'cypher'  # Matches any repo with 'cypher' in the name
    ]

    secret_manager = SecretManager()

    gcp_client = storage.Client()

    fetcher = GitHubFetcher(storage_client=gcp_client, secret_client=secret_manager)

    repos = fetcher.http_get_repos_by_patterns(org_name='neo4j',repo_patterns=repo_patterns)

    bucket = secret_manager.access_secret_version('GIT_REPOSITORIES')

    for repo_url in repos:
        fetcher.clone_and_upload_repo(repo_url, bucket)


