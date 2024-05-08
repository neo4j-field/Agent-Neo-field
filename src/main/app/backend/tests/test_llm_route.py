import unittest

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def override_get_reader():
    pass

def override_get_writer():
    pass

def override_get_embedding_service():
    pass

def override_get_llm():
    pass

class TestSession(unittest.TestCase):

    @classmethod
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

    def test_default(self) -> None:
        resp = client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), "Agent Neo backend is live.")

    def test_llm_dummy_route(self) -> None:
        resp = client.post("/llm_dummy", json=self.question)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"], "This call works!")

    def test_llm_route(self) -> None:
        pass
