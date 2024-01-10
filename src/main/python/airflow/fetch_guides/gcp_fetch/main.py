import base64

from ..fetcher import GCPFetcher
from ..fetcher import SecretManager
from google.cloud import storage
import json


if __name__ == '__main__':

    secret_manager = SecretManager(project_id='neo4j-cs-team-201901')

    secrets = secret_manager.access_secret_version('agent-neo-fetch-docs')

    service_account_info = json.loads(secrets['GOOGLE_SERVICE_ACCOUNT'])

    encoded_service_account_info = base64.b64encode(service_account_info.encode()).decode()

    gcp_client = storage.Client.from_service_account_json(encoded_service_account_info)

    fetcher = GCPFetcher(secret_manager=secret_manager, secret_name='sitemaps-secret')

    sitemaps_json = fetcher.get_sitemap_urls()
    other_articles_json = fetcher.get_other_articles()
    practitioners_guides_json = fetcher.get_practitioner_guide_md()

    other_articles_list = fetcher.extract_list_from_json(other_articles_json)
    practitioners_list = fetcher.extract_list_from_json(practitioners_guides_json)
    sitemaps_list = fetcher.extract_list_from_json(sitemaps_json)

    parsed_sitemaps_list = fetcher.parse_sitemaps_tolist(sitemaps_list)

    all_assets = GCPFetcher.concatenate_unique_ordered(parsed_sitemaps_list, practitioners_list, other_articles_list)



    output_bucket_name = 'your_output_bucket_name'
    output_file_name = 'parsed_sitemaps.txt'

    # Write the parsed sitemaps list to GCS
    fetcher.write_to_gcs(parsed_sitemaps_list, output_bucket_name, output_file_name)