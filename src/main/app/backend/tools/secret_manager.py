import json
import os
from abc import ABC, abstractmethod

from dotenv import find_dotenv, load_dotenv
from google.cloud import secretmanager


class SecretManager(ABC):
    @abstractmethod
    def access_secret_version(self, secret_id, version_id="latest"):
        pass

    @classmethod
    def from_auto(cls):
        env_path = find_dotenv()
        if env_path:
            return EnvSecretManager(env_path=env_path)
        else:
            project_id = os.getenv("GOOGLE_PROJECT_ID")
            if project_id:
                return GoogleSecretManager(project_id=project_id)
            else:
                raise EnvironmentError(
                    "Neither .env file found nor GOOGLE_PROJECT_ID set in environment variables."
                )


class EnvSecretManager(SecretManager):
    def __init__(self, env_path=None):
        if env_path:
            load_dotenv(dotenv_path=env_path)

    def access_secret_version(self, secret_id, version_id=None):
        secret = os.getenv(secret_id)
        if secret is None:
            raise KeyError(f"{secret_id} not found in environment variables")
        return secret


class GoogleSecretManager(SecretManager):
    def __init__(self, project_id):
        self.client = secretmanager.SecretManagerServiceClient()
        self.project_id = project_id

    def access_secret_version(self, secret_id, version_id="latest"):
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
        response = self.client.access_secret_version(request={"name": name})
        secret_data = response.payload.data.decode("UTF-8")
        try:
            return json.loads(secret_data)
        except json.JSONDecodeError:
            return secret_data
