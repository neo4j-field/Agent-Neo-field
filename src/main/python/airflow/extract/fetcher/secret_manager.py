from google.cloud import secretmanager
from google.oauth2 import service_account
import os
import json
import base64


class SecretManager:
    def __init__(self, service_account_info=None, project_id: str = None):
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID')

        if service_account_info:
            # If service account info is provided, create credentials from it
            credentials = service_account.Credentials.from_service_account_info(service_account_info)
            self.client = secretmanager.SecretManagerServiceClient(credentials=credentials)
        else:
            # Otherwise, use default credentials (which might be from the environment or default service account)
            self.client = secretmanager.SecretManagerServiceClient()

    def access_secret_version(self, secret_id=None, version_id="latest"):
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
        response = self.client.access_secret_version(request={"name": name})
        secret_data = response.payload.data.decode("UTF-8")
        try:
            return json.loads(secret_data)
        except json.JSONDecodeError:
            return secret_data