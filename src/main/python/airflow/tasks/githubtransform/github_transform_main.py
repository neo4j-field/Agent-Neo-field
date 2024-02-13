from google.cloud import storage

from libs.fetcher.secret_manager import SecretManager
from libs.neo4jwriter.neo4jwriter import Neo4jWriter
from libs.splitter.langchain_code_splitter import LangchainCodeSplitter
from libs.embedder.vertex_ai_embedder import VertexAIEmbedder

if __name__ == '__main__':
    secret_manager = SecretManager()
    storage_client = storage.Client()

    git_code_bucket = secret_manager.access_secret_version('GIT_REPOSITORIES_BUCKET_NAME')
    neo4j_uri = secret_manager.access_secret_version('NEO4J_URI')
    neo4j_user = secret_manager.access_secret_version('NEO4J_USER')
    neo4j_password = secret_manager.access_secret_version('NEO4J_PASSWORD')
    database = 'neo4j'

    neo4j_writer = Neo4jWriter(neo4j_url=neo4j_uri, neo4j_user=neo4j_user, neo4j_password=neo4j_password, database=database)
    splitter = LangchainCodeSplitter(secret_manager=secret_manager, storage_client=storage_client)
    vertex_ai_embedder = VertexAIEmbedder(secret_manager=secret_manager)

    for doc in splitter.read_from_gcs(bucket_name=git_code_bucket):
        embeddings = vertex_ai_embedder.embed_code([doc])
        params = [{'code': embedding['code'], 'embedding': embedding['embedding']} for embedding in embeddings]
        cypher_query = "CREATE (d:Document:Code {code: $code, embedding: $embedding})"
        neo4j_writer.batch_write(cypher_query, params)













