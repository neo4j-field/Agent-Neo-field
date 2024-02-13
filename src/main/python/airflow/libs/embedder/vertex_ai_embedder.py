from ..fetcher import SecretManager
from google.cloud import aiplatform
from typing import List, Dict, Any
from code_embedding_service import CodeEmbeddingService


class VertexAIEmbedder(CodeEmbeddingService):
    def __init__(self, secret_manager: SecretManager):
        self.secret_manager = secret_manager
        vertex_ai_config = self.secret_manager.access_secret_version("vertex_ai_config")
        self.project_id = vertex_ai_config['project_id']
        self.location = vertex_ai_config['location']
        self.endpoint_id = vertex_ai_config['endpoint_id']
        self.client_options = {"api_endpoint": f"{self.location}-aiplatform.googleapis.com"}
        self.client = aiplatform.gapic.PredictionServiceClient(client_options=self.client_options)

    def embed_code(self, code_chunks: List[str]) -> List[Dict[str, Any]]:
        embeddings = []
        for chunk in code_chunks:
            instance = {"content": chunk}
            instances = [instance]
            endpoint = self.client.endpoint_path(
                project=self.project_id, location=self.location, endpoint=self.endpoint_id)

            response = self.client.predict(endpoint=endpoint, instances=instances)

            for prediction in response.predictions:
                embedding = prediction.get('embedding')  # Adjust based on the actual response structure
                embeddings.append({'code': chunk, 'embedding': embedding})

        return embeddings
