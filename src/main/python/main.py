from scrape import Fetcher
from google.cloud import storage
import os

if __name__ == '__main__':

    service_account_key = os.getenv('GCP_SERVICE_ACCOUNT_KEY_PATH')
    sitemaps_bucket = os.getenv('GCP_SITEMAPS_BUCKET')
    practitioners_bucket = os.getenv('GCP_PRACTITIONERS_GUIDE_SITES_BUCKET')
    other_articles_bucket = os.getenv('GCP_OTHER_ARTICLES_BUCKET')


    print(sitemaps_bucket,practitioners_bucket,other_articles_bucket)


    client = storage.Client.from_service_account_json(service_account_key)
    fetch = Fetcher(client)
    test_1 = fetch.get_sitemap_urls()
    test_2 = fetch.get_other_articles()
    test_3 = fetch.get_practitioner_guide_md()
    print(test_1,test_2,test_3)