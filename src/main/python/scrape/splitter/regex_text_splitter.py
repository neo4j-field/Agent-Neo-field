import re
from typing import List
from .base_splitter import BaseSplitter, T, U

class Document:  # Placeholder for the actual Document class
    def __init__(self, page_content: str):
        self.page_content = page_content

    def copy(self):
        return Document(self.page_content)

class RegexTextSplitter(BaseSplitter[List[Document], Document]):
    def __init__(self, pattern: str):
        self.pattern = pattern

    def split(self, documents: List[Document]) -> List[Document]:
        split_docs = []
        for doc in documents:
            chunks = re.split(self.pattern, doc.page_content)
            for chunk in chunks:
                if chunk.strip():
                    new_doc = doc.copy()
                    new_doc.page_content = chunk
                    split_docs.append(new_doc)
        return split_docs
