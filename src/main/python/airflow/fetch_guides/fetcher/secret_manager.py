from google.cloud import secretmanager
import os
import json

class SecretManager:
    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID')
        self.client = secretmanager.SecretManagerServiceClient()

    def access_secret_version(self, secret_id, version_id="latest"):
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
        response = self.client.access_secret_version(request={"name": name})
        secret_data = response.payload.data.decode("UTF-8")
        try:
            return json.loads(secret_data)
        except json.JSONDecodeError:
            return secret_data