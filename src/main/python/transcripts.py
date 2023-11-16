import sys
import os
import pandas as pd
# sys.path.append("/Users/alexandergilmore/Documents/GitHub/Agent-Neo-field/src/main/python/scrape/scraper")
from scrape import WebContentChunker
from scrape.scraper.embedding import TextEmbeddingService
from scrape.scraper.preprocessing import fix_neo4j_spelling
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
    new_nodes = dict()
    i = 0
    for url, v in data.items():
        for text in v:
            new_nodes.update({str(i): {"url": url,
                                    "text": text,
                                    "embedding": embedding_service.get_embedding(text)}})
            i+=1

    print(new_nodes["0"])