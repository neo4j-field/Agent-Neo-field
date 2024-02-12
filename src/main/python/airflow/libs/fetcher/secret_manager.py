import json
import base64
from typing import Optional, Union, Dict
from google.oauth2 import service_account
from google.cloud import secretmanager


class SecretManager:
    def __init__(self, service_account_info: Optional[Union[str, Dict]] = None, project_id: Optional[str] = "sales-eng-agent-neo-project"):
        self.project_id = project_id
        if service_account_info:
            if isinstance(service_account_info, str):
                # Decode the base64-encoded string
                decoded_bytes = base64.b64decode(service_account_info)
                # Load the JSON content
                service_account_info = json.loads(decoded_bytes.decode('utf-8'))

            credentials = service_account.Credentials.from_service_account_info(service_account_info)
            self.client = secretmanager.SecretManagerServiceClient(credentials=credentials)
        else:
            self.client = secretmanager.SecretManagerServiceClient()

    def access_secret_version(self, secret_id: str, version_id: str = "latest"):
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
        response = self.client.access_secret_version(request={"name": name})
        secret_data = response.payload.data.decode("UTF-8")
        try:
            return json.loads(secret_data)
        except json.JSONDecodeError:
            return secret_data
