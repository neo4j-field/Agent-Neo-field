import unittest
from ..scraper.embedding import EmbeddingService
from langchain.embeddings.vertexai import VertexAIEmbeddings
from google.cloud import aiplatform
from google.oauth2 import service_account
import os


class TestEmbeddingService(unittest.TestCase):

    def test_generate_embedding(self):

        SERVICE_ACCOUNT = '/Users/alexanderfournier/Downloads/Agent-Neo-field/src/main/python/resources/gcp_service_account.json'

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT
        )

        aiplatform.init(project='neo4j-se-team-201905', location='us-central1',credentials=credentials)

        # Initialize the Embeddings provider
        embedding_provider = VertexAIEmbeddings()

        # Initialize the EmbeddingService with the provider
        service = EmbeddingService(embedding_provider)

        example_text = "Example text to embed"
        embedding = service.generate_embedding(example_text)
        print(embedding)

        # Assertions to check if the embedding is correct
        #self.assertIsInstance(embedding, list, "Embedding should be a list")
        #self.assertTrue(all(isinstance(x, float) for x in embedding), "Embedding should only contain floats")

if __name__ == '__main__':
    unittest.main()
