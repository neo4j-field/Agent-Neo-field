import os
import time  # Import the time module
from google.cloud import storage
from scrape import Fetcher, WebContentChunker
from scrape import parse_sitemaps_tolist, extract_list_from_json, remove_newlines, remove_unwanted_phrase
from scrape import TextEmbeddingService

if __name__ == '__main__':
    start_time = time.time()  # Start timing

    service_account_key = os.getenv('GCP_SERVICE_ACCOUNT_KEY_PATH')
    sitemaps_bucket = os.getenv('GCP_SITEMAPS_BUCKET')
    practitioners_bucket = os.getenv('GCP_PRACTITIONERS_GUIDE_SITES_BUCKET')
    other_articles_bucket = os.getenv('GCP_OTHER_ARTICLES_BUCKET')

    gcp_client = storage.Client.from_service_account_json(service_account_key)

    fetch = Fetcher(client=gcp_client)

    sitemaps_json = fetch.get_sitemap_urls()
    other_articles_json = fetch.get_other_articles()
    practitioners_guides_json = fetch.get_practitioner_guide_md()

    other_articles_list = extract_list_from_json(other_articles_json)
    practitioners_list = extract_list_from_json(practitioners_guides_json)
    sitemaps_list = extract_list_from_json(sitemaps_json)

    parsed_sitemaps_list = parse_sitemaps_tolist(sitemaps_list)

    all_assets = Fetcher.concatenate_unique_ordered(parsed_sitemaps_list, practitioners_list, other_articles_list)

    chunker = WebContentChunker()

    clean_fn = [remove_newlines, remove_unwanted_phrase]

    chunker.chunk_documents(urls=all_assets,cleaning_functions=clean_fn)

    data = chunker.chunks_as_dict

    text = data.values()

    embedding_service = TextEmbeddingService('textembedding-gecko@00')

    embeddings = embedding_service.get_embeddings_for_multiple_texts(text)

    print(embeddings)












