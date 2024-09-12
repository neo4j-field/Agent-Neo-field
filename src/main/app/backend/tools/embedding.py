import random
from typing import List, Protocol

from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel


class EmbeddingServiceProtocol(Protocol):
    def get_embedding(self, text: str) -> List[float]:
        """
        Retrieve an embedding of the provided text.
        """
        pass


class TextEmbeddingService(EmbeddingServiceProtocol):
    def __init__(self):
        self.model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
        self.aiplatform_client = aiplatform.init()

    def get_embedding(self, text: str) -> List[float]:
        embeddings = self.model.get_embeddings([text])
        return embeddings[0].values


class FakeEmbeddingService(EmbeddingServiceProtocol):
    def __init__(self, embedding_length: int = 756):
        self.embedding_length = embedding_length

    def get_embedding(self, text: str) -> List[float]:
        return [random.random() for _ in range(self.embedding_length)]
