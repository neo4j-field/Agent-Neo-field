from google.cloud import storage
from typing import Optional, Dict, Any
import os
import json
from base_fetcher import BaseFetcher


class GCPFetcher(BaseFetcher):
    def __init__(self, client: Optional[storage.Client] = None):
        super().__init__()
        self.client = client or storage.Client()

    #TODO: Fix.
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
