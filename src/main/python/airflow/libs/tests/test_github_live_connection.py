import base64
import json
import unittest


class TestGitConnectionReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env_file_path = (
            "/Users/alexanderfournier/Downloads/Agent-Neo-field/" "src/main/python/airflow/tasks/gcpfetch/env.json"
        )

        with open(env_file_path, "r") as f:
            config = json.load(f)

        cls.project_id = config.get("GCP_PROJECT_ID")
        cls.service_account_config = config.get("GOOGLE_SERVICE_ACCOUNT")
        cls.github_access_token = config.get("GITHUB_ACCESS_TOKEN")

    @classmethod
    def decode_base64_to_json(cls, base64_str):
        json_bytes = base64.b64decode(base64_str)
        json_str = json_bytes.decode("utf-8")
        data = json.loads(json_str)
        return data


if __name__ == "__main__":
    unittest.main()
