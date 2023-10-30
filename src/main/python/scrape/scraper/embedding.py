from typing import List, Callable
from langchain.schema.embeddings import Embeddings
from time import time


class EmbeddingService:
    def __init__(self, embedding_provider: Embeddings, max_retries: int = 5, retry_delay: int = 5,
                 backoff_factor: int = 2) -> None:
        self.max_retries: int = max_retries
        self.retry_delay: int = retry_delay
        self.backoff_factor: int = backoff_factor
        self.embedding_provider: Embeddings = embedding_provider

    def handle_quota_errors(self, func: Callable[..., List[float]]) -> Callable[..., List[float]]:
        def decorator(*args, **kwargs) -> List[float]:
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if retries >= self.max_retries:
                        raise
                    retries += 1
                    wait = self.retry_delay * (self.backoff_factor ** retries)
                    print(f"Retrying after error: {e}, waiting for {wait} seconds")
                    time.sleep(wait)

        return decorator

    @handle_quota_errors
    def generate_embedding(self, chunk_text: str) -> List[float]:
        return self.embedding_provider.embed_query(chunk_text)
