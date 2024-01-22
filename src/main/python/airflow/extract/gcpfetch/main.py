import base64
import json
from google.cloud import storage
from google.oauth2 import service_account
from ..fetcher import GCPFetcher, SecretManager

if __name__ == '__main__':
    secret_manager = SecretManager(project_id='neo4j-cs-team-201901')

    secrets = secret_manager.access_secret_version(secret_id='agent-neo-fetch-docs')

    # Assuming the secret is a JSON object with the base64-encoded service account key
    # Decode the base64 encoded service account info
    decoded_service_account_info = base64.b64decode(secrets['GOOGLE_SERVICE_ACCOUNT'])
    service_account_info = json.loads(decoded_service_account_info)

    # Create credentials from the service account info
    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    # Initialize the GCP client with these credentials
    gcp_client = storage.Client(credentials=credentials)

    fetcher = GCPFetcher(client=gcp_client, secret_manager=secret_manager, secret_name='sitemaps-secret')

    # grab the other keys from the json secrets.
    sitemaps_bucket = secrets['GCP_SITEMAPS_BUCKET']
    practitioners_bucket = secrets['GCP_PRACTITIONERS_GUIDE_SITES_BUCKET']
    other_articles_bucket = secrets['GCP_OTHER_ARTICLES_BUCKET']
    processed_docs_bucket = secrets['GCP_PROCESSED_DOCS']

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
