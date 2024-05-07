import random
from typing import List, Dict, Protocol

from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel


class EmbeddingServiceProtocol(Protocol):
    def get_embedding(self, text: str) -> List[float]:
        """
        Retrieve an embedding of the provided text.
        """
        pass


class TextEmbeddingService:
    def __init__(self):
        self.model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
        # self.credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

        self.aiplatform_client = aiplatform.init()
        # self.aiplatform_client.init(project='neo4j-se-team-201905', location='us-central1',
        #                             credentials=self.credentials)

    def get_embedding(self, text: str) -> List[float]:
        embeddings = self.model.get_embeddings([text])
        return embeddings[0].values

class FakeEmbeddingService:
    def get_embedding(self, text: str) -> List[float]:
        return [random.random() for _ in range(768)]
