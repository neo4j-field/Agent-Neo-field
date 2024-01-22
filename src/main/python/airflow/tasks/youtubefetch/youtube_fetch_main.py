import os
from uuid import uuid4

from google.cloud import aiplatform
from google.oauth2 import service_account


if __name__ == '__main__':

    google_credentials = service_account.Credentials.from_service_account_file(
        os.environ.get("GCP_SERVICE_ACCOUNT_KEY_PATH")
    )

    chunker = WebContentChunker()

    docs = chunker.chunk_youtube_transcripts(cleaning_functions=[fix_neo4j_spelling])

    embedding_service = TextEmbeddingService('textembedding-gecko@001',
                                             aiplatform_client=aiplatform.init(project=os.environ.get('GCP_PROJECT'),
                                                                               location=os.environ.get('GCP_REGION'),
                                                                               credentials=google_credentials))

    # create nodes to load into graph
    data = chunker.chunks_as_dict.copy()
    new_nodes = list()
    for url, v in data.items():
        for text in v:
            new_nodes.append({"index": str(uuid4()),
                              "url": url,
                              "text": text,
                              "embedding": embedding_service.get_embedding(text)})

    writer = Neo4jWriter()

    query = """
            UNWIND $params AS param
            MERGE (d:Document {index: param.index})
            MERGE (s:Source {url:param.url})
            MERGE (t:Type {type: "YouTube transcript"})
            SET
                d.createTime = datetime(),
                d.index = param.index,
                d.text = param.text,
                d.url = param.url,
                d.embedding = param.embedding
            MERGE (d)-[:HAS_SOURCE]->(s)
            MERGE (s)-[:HAS_TYPE]->(t)
            """

    writer.batch_write(cypher_query=query, params=new_nodes, batch_size=1000)

    print("YouTube transcript chunks uploaded to graph successfully.")