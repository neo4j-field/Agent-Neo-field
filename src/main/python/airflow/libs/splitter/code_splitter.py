import ast
from typing import List
from .base_splitter import BaseSplitter, T, U


class PythonCodeSplitter(BaseSplitter[str, str]):
    def __init__(self, code: str = None):
        self.tree = None
        if code:
            self.tree = ast.parse(code)

    def split(self, code: str = None) -> List[str]:
        if code:
            self.tree = ast.parse(code)
        if not self.tree:
            raise ValueError("No code to split. Provide code in constructor or split method.")

        split_code = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                func_or_class_code = ast.unparse(node)
                split_code.append(func_or_class_code)
        return split_code

