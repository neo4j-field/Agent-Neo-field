from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
from typing import List, Dict
import time
import os


class TextEmbeddingService:
    def __init__(self, model_name: str, aiplatform_client=None):
        self.model = TextEmbeddingModel.from_pretrained(model_name)
        self.credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

        self.aiplatform_client = aiplatform_client
        if self.aiplatform_client is None:
            self.aiplatform_client = aiplatform
            self.aiplatform_client.init(project='neo4j-se-team-201905', location='us-central1',
                                        credentials=self.credentials)

    def get_embedding(self, text: str) -> List[float]:
        embeddings = self.model.get_embeddings([text])
        return embeddings[0].values

    def get_embeddings_for_multiple_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.get_embeddings(texts)
        return [embedding.values for embedding in embeddings]

    def process_texts(self, texts_dict: Dict[str, str]) -> Dict[str, List[float]]:
        embeddings_dict = {}
        for url, text in texts_dict.items():
            embedding = self.get_embedding(text)
            embeddings_dict[url] = embedding
        return embeddings_dict


class LangchainEmbeddingService:
    def __init__(self, embedding_provider):
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
