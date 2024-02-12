import re
from typing import List
import ast


#TODO
#11.18 worth looking into an ABC/inteface for these two classes.
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



class CodeSplitter:
    def __init__(self, code:str):
        self.tree = ast.parse(code)

    def split_code(self) -> List[str]:
        split_code = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                func_or_class_code = ast.unparse(node)
                split_code.append(func_or_class_code)
        return split_code





