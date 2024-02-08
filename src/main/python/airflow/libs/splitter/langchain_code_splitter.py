from typing import List, Set
from ..fetcher import SecretManager
from .base_splitter import BaseSplitter, T, U
from langchain.text_splitter import (
    Language,
    RecursiveCharacterTextSplitter,
)
from google.cloud import storage
from langchain.docstore.document import Document


class LangchainCodeSplitter(BaseSplitter[str, str]):
    def __init__(self, secret_manager: SecretManager = None,
                 storage_client: storage.Client = None):
        super().__init__()
        self.secret_client = secret_manager or SecretManager()
        self.storage_client = storage_client or storage.Client()

    def _detect_language(self, file_path: str) -> Language:
        extension_to_language = {
            '.py': Language.PYTHON,
            '.js': Language.JS,
            '.java': Language.JAVA,
            '.ts': Language.TS,
            'js': Language.JS
        }
        extension = '.' + file_path.split('.')[-1]
        return extension_to_language.get(extension)

    def _list_directories_in_bucket(self, bucket_name: str) -> Set[str]:
        bucket = self.storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs()
        directories = set()
        for blob in blobs:
            directory = '/'.join(blob.name.split('/')[:-1])
            directories.add(directory)
        return directories

    def read_from_gcs(self, bucket_name: str):
        directories = self._list_directories_in_bucket(bucket_name)
        for directory in directories:
            for file_path in self._list_files_in_directory(bucket_name, directory):
                yield from self.process_file_contents(bucket_name, file_path)

    def _list_files_in_directory(self, bucket_name: str, directory: str) -> List[str]:
        bucket = self.storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=directory)
        return [blob.name for blob in blobs]

    def process_file_contents(self, bucket_name: str, file_path: str, **kwargs):
        language = self._detect_language(file_path)
        if language is None:
            return  # Skip the file if its language is not recognized

        content = self.storage_client.bucket(bucket_name).blob(file_path).download_as_text()
        content_as_list = [content]  # Keep the entire content as a single string in a list
        for processed_chunk in self.split(content_as_list, language=language, **kwargs):
            yield processed_chunk

    def split(self, input_data: List[str], **kwargs) -> List[Document]:
        chunk_size = kwargs.get('chunk_size', 250)
        chunk_overlap = kwargs.get('chunk_overlap', 0)
        language = kwargs.get('language')

        if not language:
            raise ValueError("Language must be specified")

        splitter = RecursiveCharacterTextSplitter.from_language(language, chunk_size=chunk_size,
                                                                chunk_overlap=chunk_overlap)
        return splitter.create_documents(input_data)