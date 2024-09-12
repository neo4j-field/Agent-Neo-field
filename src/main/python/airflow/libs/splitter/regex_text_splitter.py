import re
from typing import List

from google.cloud import storage

from ..fetcher import SecretManager
from .base_splitter import BaseSplitter


class Document:
    def __init__(self, page_content: str):
        self.page_content = page_content

    def copy(self):
        return Document(self.page_content)


class RegexTextSplitter(BaseSplitter[List[Document], List[Document]]):
    def __init__(
        self,
        secret_manager: SecretManager = None,
        storage_client: storage.Client = None,
        pattern: str = None,
    ):
        super().__init__()
        self.secret_client = secret_manager or SecretManager()
        self.storage_client = storage_client or storage.Client()
        self.pattern = pattern

    def split(self, documents: List[Document], *args, **kwargs) -> List[Document]:
        split_docs = []
        for doc in documents:
            chunks = re.split(self.pattern, doc.page_content)
            for chunk in chunks:
                if chunk.strip():
                    new_doc = doc.copy()
                    new_doc.page_content = chunk
                    split_docs.append(new_doc)
        return split_docs
