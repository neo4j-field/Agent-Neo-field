from google.cloud import storage
from typing import Optional, Dict, Any,List
import os
import json
from .base_fetcher import BaseFetcher
import requests
from bs4 import BeautifulSoup
from .secret_manager import SecretManager
from itertools import chain


class GCPFetcher(BaseFetcher):
    def __init__(self, storage_client: Optional[storage.Client] = None, secret_client: SecretManager = None):
        super().__init__()
        self._storage_client = storage_client or storage.Client()
        self._secret_client = secret_client or SecretManager()

    @property
    def storage_client(self):
        return self._storage_client

    @property
    def secret_manager_client(self):
        return self._secret_manager_client

    def fetch_config(self, secret_name):
        return self._secret_client.access_secret_version(secret_name)

    def fetch(self, bucket_name: Optional[str] = None) -> Dict[str, Any]:
        return self.get_sitemap_urls(bucket_name)

    def get_sitemap_urls(self, bucket_name: Optional[str] = None) -> Dict[str, Any]:
        if bucket_name is None:
            bucket_name = os.environ.get('GCP_SITEMAPS_BUCKET')
        return self._read_from_gcp(bucket_name)

    def get_practitioner_guide_md(self, bucket_name: Optional[str] = None) -> Dict[str, Any]:
        if bucket_name is None:
            bucket_name = os.environ.get('GCP_PRACTITIONERS_GUIDE_SITES_BUCKET')
        return self._read_from_gcp(bucket_name)

    def get_other_articles(self, bucket_name: Optional[str] = None) -> Dict[str, Any]:
        if bucket_name is None:
            bucket_name = os.environ.get('GCP_OTHER_ARTICLES_BUCKET')
        return self._read_from_gcp(bucket_name)

    def _read_from_gcp(self, bucket_name: str, blob_name: str = None) -> Dict[str, Any]:

        bucket = self._storage_client.get_bucket(bucket_name)

        if not blob_name:
            blobs = list(bucket.list_blobs())
            if not blobs:
                return []
            blob_name = blobs[0].name

        blob = bucket.get_blob(blob_name)

        if blob is None:
            return []

        content = blob.download_as_text()
        data = json.loads(content)
        return data

    def _parse_sitemap(self, sitemap: str) -> List[str]:
        response = requests.get(sitemap)
        soup = BeautifulSoup(response.content, "xml")
        urls = [element.text for element in soup.find_all("loc")]
        return urls

    def parse_sitemaps_tolist(self,sitemaps: List[str]) -> List[str]:
        neo4j_doc_sites = []

        for sitemap in sitemaps:
            try:
                neo4j_doc_sites.extend(self._parse_sitemap(sitemap))
            except Exception as e:
                print(f"Error parsing sitemap {sitemap}: {e}")

        return neo4j_doc_sites

    def extract_list_from_json(self,json_data: dict, key: str = None) -> list:
        if key:
            return json_data.get(key, [])
        elif len(json_data) == 1:
            single_key = next(iter(json_data.keys()))
            if isinstance(json_data[single_key], list):
                return json_data[single_key]
        return []

    def concatenate_unique_ordered(self,*lists: List[Any]) -> List[Any]:
        seen = set()
        result = []
        for item in chain.from_iterable(
                lists):
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    def write_to_gcs(self, data: List[str] = None, bucket_name: str = None, file_name: str = None):
        """
        Write data to a file in Google Cloud Storage.
        """
        bucket = self._storage_client.get_bucket(bucket_name)
        blob = bucket.blob(file_name)

        # Convert list to string for writing to file
        data_str = "\n".join(data)
        blob.upload_from_string(data_str)
        print(f"Data written to {file_name} in bucket {bucket_name}")
