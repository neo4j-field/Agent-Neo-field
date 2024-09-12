import ast
from typing import List

from google.cloud import storage

from ..fetcher import SecretManager
from .base_splitter import BaseSplitter


class PythonCodeSplitter(BaseSplitter[str, str]):
    def __init__(
        self,
        secret_manager: SecretManager = None,
        storage_client: storage.Client = None,
    ):
        super().__init__()
        self.secret_client = secret_manager or SecretManager()
        self.storage_client = storage_client or storage.Client()

    def split(self, code: str = None, *args, **kwargs) -> List[str]:
        """
        Splits the provided Python code or the code passed during initialization
        into function and class definitions.

        :param code: Optional Python code to split.
        :return: A list of strings representing function and class definitions.
        """
        if code:
            self.tree = ast.parse(code)
        if not self.tree:
            raise ValueError("No code to split. Provide code in constructor or split method.")

        split_code = []
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                func_or_class_code = ast.unparse(node)
                split_code.append(func_or_class_code)
        return split_code
