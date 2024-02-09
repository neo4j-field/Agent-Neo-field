from google.cloud import storage
import json

import pandas as pd

from google.oauth2 import service_account
from langchain_google_vertexai import VertexAIEmbeddings

from helpers import batch_method, prepare_new_nodes
from libs.embedding.embedding import LangchainEmbeddingService
from libs.fetcher.secret_manager import SecretManager
from libs.transformer.youtube_transformer import YouTubeTransformer
from libs.neo4jwriter.neo4jwriter import Neo4jWriter



if __name__ == "__main__":
    secret_manager = SecretManager(project_id='sales-eng-agent-neo-project')

    service_account_info = secret_manager.access_secret_version('GCP_SERVICE_ACCOUNT')

    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    gcp_client = storage.Client(credentials=credentials)
    loader = YouTubeTransformer(storage_client=gcp_client, secret_client=secret_manager)

    bucket = gcp_client.get_bucket("agent-neo-youtube")
    # with open("scrape/scraper/resources/youtube_playlist_ids.json") as json_file:
    #     playlists = json.load(json_file)
    playlists = bucket.get_blob("youtube_playlist_ids.json")
    playlists = json.loads(playlists.download_as_string())

    vertex = VertexAIEmbeddings(credentials=credentials, 
                            project='sales-eng-agent-neo-project', 
                            location=secret_manager.access_secret_version('gcp_region'),
                            model_name="textembedding-gecko@001")

    embedding_service = LangchainEmbeddingService(vertex)

    transformer = YouTubeTransformer(storage_client=gcp_client, secret_client=secret_manager)
    writer = Neo4jWriter()

    query = """
            UNWIND $params AS param

            MERGE (d:Document {index: param.index})
            MERGE (s:Source {url: param.url})
            MERGE (t:Type {type: "YouTube transcript"})
            SET
                d.createTime = datetime(),
                d.text = param.transcript,
                d.url = param.url,
                d.embedding = param.embedding,
                
                s.title = param.title,
                s.playlist_id = param.playlist_id,
                s.video_id = param.video_id,
                s.publish_date = param.publish_date
                
            MERGE (d)-[:HAS_SOURCE]->(s)
            MERGE (s)-[:HAS_TYPE]->(t)
            """
    
    for playlist, pl_id in playlists.items():

        transformer._chunked_documents = []
        transformer.chunk_youtube_transcripts(playlist_title=playlist)
        
        result = []
        failed_idx = None
        playlist_total = len(transformer.youtube_chunks_as_list)

        print(playlist, playlist_total)
        print("grabbing embeddings...")
        for idx, batch in enumerate(batch_method(transformer.youtube_chunks_as_list, 20)):
            new_nodes, failed_idx = prepare_new_nodes(data=batch, embedding_service=embedding_service, playlist_id=pl_id)
            result+=new_nodes
            print("total percent: ", str(round(((20*idx)+1) / playlist_total, 4)*100)[:4], "%", " batch", idx+1, end="\r")

        print("chunks processed: ", len(result))
        if failed_idx is not None:
            print("playlist     : ", playlist)
            print("failed index : ", failed_idx)

        print("loading to graph...")
        writer.batch_write(cypher_query=query, params=result, batch_size=100)

        print("playlist upload complete!")