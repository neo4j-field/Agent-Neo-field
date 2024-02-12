from google.cloud import storage

from libs.fetcher.secret_manager import SecretManager
from libs.fetcher.gcp_fetcher import GCPFetcher
from libs.neo4jwriter.neo4jwriter import Neo4jWriter

#todo: Implement maybe an encoder class that returns a list of perhaps 1000 embeddings.
if __name__ == '__main__':


    secret_manager = SecretManager()

    storage_client = storage.Client()

    fetcher = GCPFetcher()

    gitcode_bucket = secret_manager.access_secret_version('GIT_REPOSITORIES')

    splitter = LangchainCodeSplitter(secret_manager=secret_manager, storage_client=storage_client)

    for doc in splitter.read_from_gcs(bucket_name=bucket_name):
        pass




