from .base_fetcher import BaseFetcher
from .secret_manager import SecretManager
from typing import Optional
from google.cloud import storage
from typing import List,Dict
import re
import requests

class GitHubFetcher(BaseFetcher):
    def __init__(self, storage_client: Optional[storage.Client] = None, secret_client: SecretManager = None):
        super().__init__()
        self._storage_client = storage_client or storage.Client()
        self._secret_client = secret_client or SecretManager()
        secret_data = self._secret_client.access_secret_version('GITHUB_ACCESS_TOKEN')
        self.github_token = secret_data



    @property
    def storage_client(self):
        return self._storage_client

    @property
    def secret_manager_client(self):
        return self._secret_manager_client

    def fetch_config(self, secret_name):
        return self._secret_client.access_secret_version(secret_name)



    def fetch_files_from_git_repos(self, org_name: str, repo_pattern: str) -> Dict[str, str]:
        file_contents = {}
        repo_urls = self._get_git_repos_by_pattern(org_name=org_name, repo_pattern=repo_pattern)

        repo_names = [repo_url.split('/')[-1].split('.')[0] for repo_url in repo_urls]

        for repo_name in repo_names:
            repo_files = self._list_repo_files(org_name=org_name, repo_name=repo_name)
            for file_path, file_url in repo_files.items():
                file_data = self._fetch_file_content(file_url)
                if file_data:
                    file_contents[f"{repo_name}/{file_path}"] = file_data
        return file_contents

    def _get_git_repos_by_pattern(self, org_name: str, repo_pattern: str) -> List[str]:
        all_repos = self.list_github_repos(org_name=org_name)
        return [repo for repo in all_repos if re.search(repo_pattern, repo)]

    def list_github_repos(self, org_name: str) -> List[str]:
        headers = {'Authorization': f'token {self.github_token}'}
        repo_urls = []
        page = 1
        while True:
            response = requests.get(f'https://api.github.com/orgs/{org_name}/repos?page={page}', headers=headers)
            data = response.json()
            if not data:
                break
            repo_urls.extend([repo['clone_url'] for repo in data])
            page += 1
        return repo_urls

    def _list_repo_files(self, org_name: str, repo_name: str) -> Dict[str, str]:
        api_base_url = f"https://api.github.com/repos/{org_name}/{repo_name}/contents/"
        file_paths = self._recursive_file_listing(api_base_url)
        return file_paths

    def _recursive_file_listing(self, url: str, path: str = '') -> Dict[str, str]:
        headers = {'Authorization': f'token {self.github_token}'}
        response = requests.get(url + path, headers=headers)
        items = response.json()

        file_paths = {}
        if isinstance(items, list):
            for item in items:
                if item['type'] == 'file':
                    file_paths[item['path']] = item['url']
                elif item['type'] == 'dir':
                    file_paths.update(self._recursive_file_listing(url, item['path']))
        return file_paths

    def _fetch_file_content(self, file_url):
        try:
            response = requests.get(file_url)
            response.raise_for_status()
            file_data = response.content

            encoding = 'iso-8859-1'

            decoded_content = file_data.decode(encoding)

            return decoded_content

        except Exception as e:
            # Handle any exceptions here
            print(f"Error fetching or decoding file: {str(e)}")
            return None