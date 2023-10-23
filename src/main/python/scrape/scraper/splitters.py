import re
from typing import List


#TODO: Implement more complex Splitters based on research
class RegexTextSplitter:

    def __init__(self, pattern: str):
        self.pattern = pattern

    def split_documents(self, documents: List['Document']) -> List['Document']:
        split_docs = []
        for doc in documents:
            chunks = re.split(self.pattern, doc.page_content)
            for chunk in chunks:
                if chunk.strip():  # Avoiding empty documents
                    # Copy metadata and set the chunked content
                    new_doc = doc.copy()
                    new_doc.page_content = chunk
                    split_docs.append(new_doc)
        return split_docs
