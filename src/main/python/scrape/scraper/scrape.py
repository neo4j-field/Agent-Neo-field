from typing import List, Callable, Dict,Any
import requests
from bs4 import BeautifulSoup
from typing import List
from itertools import chain
import langchain
from langchain.document_loaders import UnstructuredURLLoader
from langchain.schema.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import VertexAIEmbeddings
from google.cloud import storage
import json
import os


class Fetcher:
    def __init__(self, gcp_client: storage.Client = None):
        self.client = gcp_client or storage.Client()
        self.service_account = os.environ.get('GCP_SERVICE_ACCOUNT_KEY_PATH')

    def get_sitemap_urls(self) -> Dict[str, Any]:
        bucket_name = os.environ.get('GCP_SITEMAPS_BUCKET')
        return self._read_from_gcp(bucket_name)

    def get_practitioner_guide_md(self) -> Dict[str, Any]:
        bucket_name = os.environ.get('GCP_PRACTITIONERS_GUIDE_SITES_BUCKET')
        return self._read_from_gcp(bucket_name)

    def get_other_articles(self) -> Dict[str, Any]:
        bucket_name = os.environ.get('GCP_OTHER_ARTICLES_BUCKET')
        return self._read_from_gcp(bucket_name)


    def _read_from_gcp(self, bucket_name: str, blob_name: str = None) -> Dict[str, Any]:
        """Read data from a GCP bucket and return it as a list of strings."""

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

    @staticmethod
    def concatenate_unique_ordered(self,*lists: List) -> List:
        seen = set()
        result = []
        for item in chain(*lists):
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result




class WebContentChunker:
    def __init__(self):
        self._chunked_documents = None

    @property
    def chunk_texts(self) -> List[str]:
        """
        Returns the list of page_content from all chunked documents.
        """
        if not self._chunked_documents:
            raise ValueError("Documents have not been chunked yet. Call chunk_documents() first.")
        return [chunk.page_content for chunk in self._chunked_documents]

    @property
    def chunk_urls(self) -> List[str]:
        """
        Returns the list of source URLs from the metadata of all chunked documents.
        """
        if not self._chunked_documents:
            raise ValueError("Documents have not been chunked yet. Call chunk_documents() first.")
        return [chunk.metadata['source'] for chunk in self._chunked_documents]

    def scrape_sites_into_langchain_docs(self) -> List[Document]:
        documents = None
        try:
            loader = UnstructuredURLLoader(self._docs)
            documents = loader.load()
        except Exception as e:
            print(f"Error loading documents from URLs: {e}")
        return documents

    def chunk_documents(self, splitter: Callable[[List[Document]], List[Document]] = None) -> List[Document]:
        if splitter is None:
            splitter = CharacterTextSplitter(
                separator="\n",
                chunk_size=1024,  # ref https://www.pinecone.io/learn/chunking-strategies/
                chunk_overlap=128  # set approx 15% overlap between chunked documents
            )

        documents = self.scrape_sites_into_langchain_docs()
        split_documents = splitter.split_documents(documents)
        return split_documents

    def __str__(self):
        doc_strings = [str(doc) for doc in self._docs]
        return "\n".join(["ScrapeLangChain Documents:"] + doc_strings)
