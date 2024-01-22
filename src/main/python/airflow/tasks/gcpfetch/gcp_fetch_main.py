import base64
import json
from google.cloud import storage
from google.oauth2 import service_account
from ..fetcher import GCPFetcher, SecretManager

if __name__ == '__main__':
    secret_manager = SecretManager(project_id='neo4j-cs-team-201901')

    service_account_info = secret_manager.access_secret_version('GCP_SERVICE_ACCOUNT')

    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    gcp_client = storage.Client(credentials=credentials)

    fetcher = GCPFetcher(client=gcp_client, secret_manager=secret_manager)

    sitemaps_bucket = secret_manager.access_secret_version('GCP_SITEMAPS_BUCKET')
    practitioners_bucket = secret_manager.access_secret_version('GCP_PRACTITIONERS_GUIDE_SITES_BUCKET')
    other_articles_bucket = secret_manager.access_secret_version('GCP_OTHER_ARTICLES_BUCKET')
    processed_docs_bucket = secret_manager.access_secret_version('GCP_PROCESSED_DOCS')

    sitemaps_json = fetcher.get_sitemap_urls(bucket_name=sitemaps_bucket)
    other_articles_json = fetcher.get_other_articles(bucket_name=other_articles_bucket)
    practitioners_guides_json = fetcher.get_practitioner_guide_md(bucket_name=practitioners_bucket)

    other_articles_list = fetcher.extract_list_from_json(other_articles_json)
    practitioners_list = fetcher.extract_list_from_json(practitioners_guides_json)
    sitemaps_list = fetcher.extract_list_from_json(sitemaps_json)

    parsed_sitemaps_list = fetcher.parse_sitemaps_tolist(sitemaps_list)

    all_assets = GCPFetcher.concatenate_unique_ordered(parsed_sitemaps_list, practitioners_list, other_articles_list)

    output_file_name = 'all_assets.txt'

    fetcher.write_to_gcs(data=all_assets,bucket_name=processed_docs_bucket, output_file_name=output_file_name)
