from .base_fetcher import BaseFetcher
from .secret_manager import SecretManager
from typing import Optional
from google.cloud import storage

class GitHubFetcher(BaseFetcher):
    def __init__(self, storage_client: Optional[storage.Client] = None, secret_client: SecretManager = None):
        super().__init__()
        self._storage_client = storage_client or storage.Client()
        self._secret_client = secret_client or SecretManager()