from google.cloud import storage
import json

import pandas as pd

from google.oauth2 import service_account
from libs.fetcher.secret_manager import SecretManager
from libs.fetcher.youtube_fetcher import YoutubeFetcher



if __name__ == "__main__":
    secret_manager = SecretManager(project_id='sales-eng-agent-neo-project')

    service_account_info = secret_manager.access_secret_version('GCP_SERVICE_ACCOUNT')

    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    gcp_client = storage.Client(credentials=credentials)
    loader = YoutubeFetcher(storage_client=gcp_client, secret_client=secret_manager)

    bucket = gcp_client.get_bucket("agent-neo-youtube")
    # with open("scrape/scraper/resources/youtube_playlist_ids.json") as json_file:
    #     playlists = json.load(json_file)
    playlists = bucket.get_blob("youtube_playlist_ids.json")
    playlists = json.loads(playlists.download_as_string())

    for title, id in playlists.items():
        # set playlist id
        loader.playlist_id = id
        loader._scraped_video_info = None
        print(title)
        print(loader.playlist_id)

        print("creating CSV file with video info...")
        # scrape video info for playlist
        loader.scrape_video_info(videos=[])

        print("uploading CSV file to Storage...")
        # upload to Storage
        loader.upload_scraped_video_info(file_name=title)

        print("Creating and uploading transcripts...")
        # create and upload transcripts
        loader.create_and_upload_neo4j_transcripts(transcripts_folder=title, video_info_file_name=title)












'''
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


'''