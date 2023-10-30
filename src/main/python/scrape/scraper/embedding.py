from typing import List, Callable
from langchain.schema.embeddings import Embeddings
from time import time


class EmbeddingService:
    def __init__(self, embedding_provider) -> None:
        self.embedding_provider = embedding_provider

    def handle_quota_errors(func):
        def wrapper(self, *args, **kwargs):
            max_retries, retry_delay, backoff_factor = 5, 5, 2
            retries = 0
            while True:
                try:
                    # Call the function with the provided args and kwargs
                    return func(self, *args, **kwargs)
                except Exception as e:
                    if retries >= max_retries:
                        raise
                    retries += 1
                    wait = retry_delay * (backoff_factor ** retries)
                    print(f"Retrying after error: {e}, waiting for {wait} seconds")
                    time.sleep(wait)
        return wrapper

    @handle_quota_errors
    def generate_embedding(self, chunk_text: str) -> List[float]:
        return self.embedding_provider.embed_query(chunk_text)