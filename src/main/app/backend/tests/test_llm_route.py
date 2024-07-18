#todo: this is broken now. I am getting the following error:
#todo: I think it's related to DI the secret manager... or somehow my IDE isn't picking up something
'''
raise KeyError(f"{secret_id} not found in environment variables")
KeyError: 'OPENAI_API_KEY not found in environment variables'
'''


import sys
import os
import unittest
from unittest.mock import patch
import inspect

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
import pandas as pd
from typing import List, Tuple

from main import app
from database import GraphReader, GraphWriter
from tools import FakeEmbeddingService
from tools import LLM
from tools import SecretManager
from objects.graphtypes import UserMessage, AssistantMessage
from objects.rating import Rating
from routers.llm import get_embedding_service, get_llm, get_reader, get_writer

client = TestClient(app)


class MockSecretManager(SecretManager):

    def __init__(self, secret_id):
        self.secret_id = secret_id

    def access_secret_version(self, secret_id, version_id="latest"):
        secrets = {
            'OPENAI_API_KEY': 'test-key',
            'OPENAI_API_VERSION': 'v1',
            'NEO4J_URI': 'neo4j://localhost:7687',
            'NEO4J_USERNAME': 'neo4j',
            'NEO4J_PASSWORD': 'password',
            'NEO4J_DATABASE': 'neo4j',
            'GCP_PROJECT_ID': 'test-project',
            'GCP_REGION': 'us-central1',
        }
        return secrets.get(self.secret_id, 'default-value')


class GraphWriterMock(GraphWriter):
    def __init__(self):
        super().__init__(secret_manager=MockSecretManager(secret_id='OPEN_API_KEY'))

    def log_new_conversation(
            self, message: UserMessage, llm_type: str, temperature: float
    ) -> None:
        pass

    def log_user(self, message: UserMessage, previous_message_id: str) -> None:
        pass

    def log_assistant(
            self,
            message: AssistantMessage,
            previous_message_id: str,
            context_ids: List[str],
    ) -> None:
        pass

    def rate_message(rating: Rating) -> None:
        pass


class GraphReaderMock(GraphReader):
    def __init__(self):
        super().__init__(secret_manager=MockSecretManager(secret_id='OPEN_API_KEY'))

    def retrieve_context_documents(
            self, question_embedding: List[float], number_of_context_documents: int = 10
    ) -> pd.DataFrame:
        return pd.DataFrame.from_dict(
            {
                "index": ["a", "b", "c"],
                "text": ["text a", "text b", "text c"],
                "url": ["http://a", "http://b", "http://c"],
            }
        )

    def retrieve_conversation_history(self, conversation_id: str) -> List[Tuple[Tuple[List, List], Tuple[List, List]]]:
        return [
            (
                ([
                     {"community": 1, "contextCount": 1, "embedding": [0.1, 0.2], "fast_rp_similarity": [0.3],
                      "index": 1, "pageRank": 0.5, "text": "text1", "url": "url1"}
                 ], [
                     {"start_node": {"community": 1, "contextCount": 1, "embedding": [0.1, 0.2],
                                     "fast_rp_similarity": [0.3], "index": 1, "pageRank": 0.5, "text": "text1",
                                     "url": "url1"},
                      "end_node": {"community": 2, "contextCount": 2, "embedding": [0.2, 0.3],
                                   "fast_rp_similarity": [0.4], "index": 2, "pageRank": 0.6, "text": "text2",
                                   "url": "url2"}}
                 ]),
                ([
                     {"content": "content1", "id": "msg1", "post_time": "time1", "role": "user"}
                 ], [
                     {"start_node": {"content": "content1", "id": "msg1", "post_time": "time1", "role": "user"},
                      "end_node": {"content": "content2", "id": "msg2", "post_time": "time2", "role": "assistant"}}
                 ])
            )
        ]


def override_get_secret_manager():
    return MockSecretManager(secret_id='OPEN_API_KEY')


def override_get_reader():
    return GraphReaderMock()


def override_get_writer():
    return GraphWriterMock()


def override_get_embedding_service():
    return FakeEmbeddingService()


def override_get_llm():
    return LLM(llm_type="fake", temperature=0)


app.dependency_overrides[get_reader] = override_get_reader
app.dependency_overrides[get_writer] = override_get_writer
app.dependency_overrides[get_embedding_service] = override_get_embedding_service
app.dependency_overrides[get_llm] = override_get_llm
app.dependency_overrides[SecretManager] = MockSecretManager


class TestLLMRoute(unittest.TestCase):

    @classmethod
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def setUpClass(cls) -> None:
        cls.question = {
            "session_id": "s-123-test",
            "conversation_id": "conv-123-test",
            "message_id": "user-123-test",
            "question": "What is GDS?",
            "conversation_history": "The user keeps asking what GDS is.",
            "llm_type": "GPT-4 8k",
            "number_of_documents": 10,
            "temperature": 0.7,
        }

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_default(self) -> None:
        print(f"Environment Variables in {inspect.currentframe().f_code.co_name}:", os.environ.get('OPENAI_API_KEY'))
        resp = client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), "Agent Neo backend is live.")

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_llm_dummy_route(self) -> None:
        print(f"Environment Variables in {inspect.currentframe().f_code.co_name}:", os.environ.get('OPENAI_API_KEY'))
        resp = client.post("/llm_dummy", json=self.question)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"], "This call works!")

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_llm_route(self) -> None:
        print(f"Environment Variables in {inspect.currentframe().f_code.co_name}:", os.environ.get('OPENAI_API_KEY'))
        resp = client.post("/llm", json=self.question)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"], "GDS is cool.")


class TestGraphResponseRoute(unittest.TestCase):

    @classmethod
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def setUpClass(cls) -> None:
        cls.conversation_id = "conv-eb834761-d076-4ffb-ab54-905a6126ee5a"

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_get_graph_response(self) -> None:
        print(f"Environment Variables in {inspect.currentframe().f_code.co_name}:", os.environ.get('OPENAI_API_KEY'))

        response = client.get(f"/graph-llm/{self.conversation_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "conversation_entries": [
                {
                    "document_nodes": [
                        {
                            "community": 1,
                            "contextCount": 1,
                            "embedding": [0.1, 0.2],
                            "fast_rp_similarity": [0.3],
                            "index": 1,
                            "pageRank": 0.5,
                            "text": "text1",
                            "url": "url1"
                        }
                    ],
                    "message_nodes": [
                        {
                            "content": "content1",
                            "id": "msg1",
                            "post_time": "time1",
                            "role": "user"
                        }
                    ],
                    "document_relationships": [],
                    "message_relationships": []
                }
            ]
        })

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_default(self) -> None:
        print(f"Environment Variables in {inspect.currentframe().f_code.co_name}:", os.environ.get('OPENAI_API_KEY'))
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Agent Neo backend is live.")


if __name__ == '__main__':
    unittest.main()
