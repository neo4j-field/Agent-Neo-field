import os
from scrape import Fetcher
from google.cloud import storage
from scrape import parse_sitemaps_tolist,parse_sitemap,concatenate_unique_ordered,extract_list_from_json

if __name__ == '__main__':
    service_account_key = os.getenv('GCP_SERVICE_ACCOUNT_KEY_PATH')
    sitemaps_bucket = os.getenv('GCP_SITEMAPS_BUCKET')
    practitioners_bucket = os.getenv('GCP_PRACTITIONERS_GUIDE_SITES_BUCKET')
    other_articles_bucket = os.getenv('GCP_OTHER_ARTICLES_BUCKET')

    client = storage.Client.from_service_account_json(service_account_key)

    fetch = Fetcher(client)
    sitemaps_json = fetch.get_sitemap_urls()
    other_articles_json = fetch.get_other_articles()
    practitioners_guides_json = fetch.get_practitioner_guide_md()

    #preprocessing
    sitemaps_list = extract_list_from_json(sitemaps_json)
    other_articles_list = extract_list_from_json(other_articles_json)
    practitioners_list = extract_list_from_json(practitioners_guides_json)








