from typing import List, Callable, Dict, Any
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
import time


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
    def concatenate_unique_ordered(*lists: List) -> List:
        seen = set()
        result = []
        for item in chain(*lists):
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result


class WebContentChunker:
    def __init__(self):
        self._chunked_documents = []

    @property
    def chunk_texts(self) -> List[str]:
        self._assert_documents_chunked()
        return [chunk.page_content for chunk in self._chunked_documents]

    @property
    def chunk_urls(self) -> List[str]:
        self._assert_documents_chunked()
        return [chunk.metadata.get('source', '') for chunk in self._chunked_documents]

    @property
    def chunks_as_dict(self) -> Dict[str, str]:
        self._assert_documents_chunked()
        return dict(zip(self.chunk_urls, self.chunk_texts))

    def _assert_documents_chunked(self):
        if not self._chunked_documents:
            raise ValueError("Documents have not been chunked yet. Call chunk_documents() first.")

    def _scrape_sites_into_langchain_docs(self, resources: List[str]) -> List[Document]:
        try:
            loader = UnstructuredURLLoader(urls=resources)
            return loader.load()
        except Exception as e:
            print(f"Error loading documents from URLs: {e}")
            return []

    def _split_into_chunks(self, documents: List[Document],
                           splitter: Callable[[List[Document]], List[Document]]) -> List[Document]:
        return splitter.split_documents(documents)

    def _clean_chunked_documents(self, chunked_docs: List[Document], cleaning_functions: List[Callable[[str], str]]) -> \
    List[Document]:
        for i, doc in enumerate(chunked_docs):
            for func in cleaning_functions:
                doc.page_content = func(doc.page_content)
            chunked_docs[i] = doc
        return chunked_docs

    def chunk_documents(self, urls: List[str],
                        splitter: Callable[[List[Document]], List[Document]] = None,
                        cleaning_functions: List[Callable[[str], str]] = None) -> None:

        chunking_start_time = time.time()  # Start timing the chunking process

        if splitter is None:
            splitter = CharacterTextSplitter(
                separator="\n",
                chunk_size=1024,
                chunk_overlap=128)

        # Start scraping
        documents = self._scrape_sites_into_langchain_docs(urls)

        # After scraping
        scraping_end_time = time.time()
        print(f"Scraping Time: {scraping_end_time - chunking_start_time} seconds")

        # Start splitting
        chunked_docs = self._split_into_chunks(documents, splitter)

        # After splitting
        splitting_end_time = time.time()
        print(f"Splitting Time: {splitting_end_time - scraping_end_time} seconds")

        if cleaning_functions:
            # Start cleaning
            chunked_docs = self._clean_chunked_documents(chunked_docs, cleaning_functions)

            # After cleaning
            cleaning_end_time = time.time()
            print(f"Cleaning Time: {cleaning_end_time - splitting_end_time} seconds")

        self._chunked_documents.extend(chunked_docs)

    def __str__(self) -> str:
        return "\n".join([f"Document: {doc}" for doc in self._chunked_documents])
