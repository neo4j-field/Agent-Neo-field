import os
import json
from google.cloud import secretmanager
from dotenv import load_dotenv


class SecretManager:
    def __init__(self, project_id: str = None, use_env: bool = False, env_path: str = None):
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID')
        self.use_env = use_env
        if self.use_env and env_path:
            load_dotenv(dotenv_path=env_path)
            for key in os.environ:
                print(f"{key}: {os.getenv(key)}")

        if not self.use_env:
            self.client = secretmanager.SecretManagerServiceClient()

    def access_secret_version(self, secret_id, version_id="latest"):
        if self.use_env:
            secret = os.getenv(secret_id)
            if secret is None:
                raise KeyError(f"{secret_id} not found in env variables")
        else:
            # Access the secret from Google Secret Manager
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
            response = self.client.access_secret_version(request={"name": name})
            secret_data = response.payload.data.decode("UTF-8")
            try:
                return json.loads(secret_data)
            except json.JSONDecodeError:
                return secret_data