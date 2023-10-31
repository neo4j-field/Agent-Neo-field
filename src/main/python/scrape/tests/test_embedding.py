import unittest
from ..scraper.embedding import TextEmbeddingService
from langchain.embeddings.vertexai import VertexAIEmbeddings
from google.cloud import aiplatform
from google.oauth2 import service_account
import os


class TestEmbeddingService(unittest.TestCase):

    def test_text_embeddings_vertexAI_lib(self):
        SERVICE_ACCOUNT = '/Users/alexanderfournier/Downloads/Agent-Neo-field/src/main/python/resources/gcp_service_account.json'

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT
        )

        aiplatform.init(project='neo4j-se-team-201905', location='us-central1', credentials=credentials)

        embedding_service = TextEmbeddingService("textembedding-gecko@001")

        texts_dict = {
            'https://neo4j.com/docs/graph-data-science-client/current/': 'For a high level explanation of how the Cypher API maps to the Python client API please see Mapping between Cypher and Python...\nWas this page helpful?',
            'https://neo4j.com/docs/graph-data-science-client/current/algorithms/': 'To do more advanced matching beyond the capabilities of find_node_id() we recommend using Cypher’s MATCH via gds.run_cypher...\nWas this page helpful?'
        }

        embeddings_dict = embedding_service.process_texts(texts_dict)
        print(embeddings_dict)

    def test_embeddings(self):
        embedding_service = TextEmbeddingService("textembedding-gecko@001")

        texts_dict = {
            'https://neo4j.com/docs/graph-data-science-client/current/': 'For a high level explanation of how the Cypher API maps to the Python client API please see Mapping between Cypher and Python...\nWas this page helpful?',
            'https://neo4j.com/docs/graph-data-science-client/current/algorithms/': 'To do more advanced matching beyond the capabilities of find_node_id() we recommend using Cypher’s MATCH via gds.run_cypher...\nWas this page helpful?'
        }

        embeddings_dict = embedding_service.process_texts(texts_dict)
        print(embeddings_dict)


if __name__ == '__main__':
    unittest.main()
