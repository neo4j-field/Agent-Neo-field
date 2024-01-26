from .base_fetcher import BaseFetcher
from .secret_manager import SecretManager
from typing import Optional, Any
from google.cloud import storage
from typing import List,Dict
import re
import requests
import os
import shutil
import subprocess

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

    def fetch(self, *args, **kwargs) -> Any:
        pass

    def http_get_repos_by_patterns(self, org_name: str, repo_patterns: List[str]) -> List[str]:
        all_repos = self.http_list_github_repos(org_name=org_name)
        compiled_patterns = [re.compile(pattern) for pattern in repo_patterns]
        matched_repos = [repo for repo in all_repos if any(pattern.search(repo) for pattern in compiled_patterns)]
        return matched_repos


    def http_list_github_repos(self, org_name: str) -> List[str]:
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

    def clone_and_upload_repo(self, repo_url: str, bucket_name: str):
        repo_name = repo_url.split('/')[-1].replace('.git', '')

        local_dir = f"/tmp/{repo_name}"  # Use repo_name in the directory path
        if os.path.exists(local_dir):
            shutil.rmtree(local_dir)
        os.makedirs(local_dir)

        subprocess.run(["git", "clone", repo_url, local_dir], check=True)

        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_file_path, local_dir)
                gcs_path = os.path.join(repo_name, relative_path)
                self._upload_file_to_gcs(local_file_path, bucket_name, gcs_path)

        shutil.rmtree(local_dir)

    def _upload_file_to_gcs(self, file_path: str, bucket_name: str, blob_name: str):
        bucket = self._storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        print(f"Uploaded {file_path} to gs://{bucket_name}/{blob_name}")


    def get_files_from_git_repos(self, org_name: str, repo_pattern: str) -> Dict[str, str]:
        file_contents = {}
        repo_urls = self.http_get_github_repos_by_pattern(org_name=org_name, repo_pattern=repo_pattern)

        repo_names = [repo_url.split('/')[-1].split('.')[0] for repo_url in repo_urls]

        for repo_name in repo_names:
            repo_files = self.http_get_github_repos(org_name=org_name, repo_name=repo_name)
            for file_path, file_url in repo_files.items():
                file_data = self._get_file_content(file_url)
                if file_data:
                    file_contents[f"{repo_name}/{file_path}"] = file_data
        return file_contents

    def http_get_repository_files(self, org_name: str, repo_name: str) -> Dict[str, str]:
        api_base_url = f"https://api.github.com/repos/{org_name}/{repo_name}/contents/"
        file_paths = self.recursive_traverse_file_hierarchy(api_base_url)
        return file_paths

    def recursive_traverse_file_hierarchy(self, url: str, path: str = '') -> Dict[str, str]:
        headers = {'Authorization': f'token {self.github_token}'}
        response = requests.get(url + path, headers=headers)
        items = response.json()

        file_paths = {}
        if isinstance(items, list):
            for item in items:
                if item['type'] == 'file':
                    file_paths[item['path']] = item['url']
                elif item['type'] == 'dir':
                    file_paths.update(self.recursive_traverse_file_hierarchy(url, item['path']))
        return file_paths

    def _get_file_content(self, file_url):
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