from google.cloud import storage
from typing import Optional, Dict, Any,List
import os
import json
from .base_fetcher import BaseFetcher
import requests
from bs4 import BeautifulSoup
from .secret_manager import SecretManager


class GCPFetcher(BaseFetcher):
    def __init__(self, client: Optional[storage.Client] = None, secret_manager: SecretManager = None, secret_name: str = None):
        super().__init__()
        self.client = client or storage.Client()
        self.secret_manager = secret_manager or SecretManager()
        self.config = self.fetch_config(secret_name) if secret_name else {}

    def fetch_config(self, secret_name):
        return self.secret_manager.access_secret_version(secret_name)

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

        bucket = self.client.get_bucket(bucket_name)

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

    def _parse_sitemaps_tolist(self,sitemaps: List[str]) -> List[str]:
        neo4j_doc_sites = []

        for sitemap in sitemaps:
            try:
                neo4j_doc_sites.extend(self._parse_sitemap(sitemap))
            except Exception as e:
                print(f"Error parsing sitemap {sitemap}: {e}")

        return neo4j_doc_sites


    def write_to_gcs(self, data: List[str] = None, bucket_name: str = None, file_name: str = None):
        """
        Write data to a file in Google Cloud Storage.
        """
        bucket = self.client.get_bucket(bucket_name)
        blob = bucket.blob(file_name)

        # Convert list to string for writing to file
        data_str = "\n".join(data)
        blob.upload_from_string(data_str)
        print(f"Data written to {file_name} in bucket {bucket_name}")
