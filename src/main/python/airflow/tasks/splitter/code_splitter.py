import ast
from typing import List
from .base_splitter import BaseSplitter, T, U


class CodeSplitter(BaseSplitter[str, str]):
    def __init__(self, code: str):
        self.tree = ast.parse(code)

    def split(self, code: str) -> List[str]:
        split_code = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                func_or_class_code = ast.unparse(node)
                split_code.append(func_or_class_code)
        return split_code
