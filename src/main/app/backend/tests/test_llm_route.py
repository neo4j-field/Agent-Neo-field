import unittest
from typing import List

from fastapi.testclient import TestClient
import pandas as pd

from main import app
from tools.embedding import FakeEmbeddingService
from tools.llm import LLM
from objects.nodes import UserMessage, AssistantMessage
from objects.rating import Rating
from routers.llm import get_embedding_service, get_llm, get_reader, get_writer

client = TestClient(app)


class GraphWriterMock:
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

class GraphReaderMock:
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


def override_get_reader():
    return GraphReaderMock()


def override_get_writer():
    return GraphWriterMock()


def override_get_embedding_service():
    return FakeEmbeddingService()


def override_get_llm():
    return LLM(llm_type="fake", temperature=0)


app.dependency_overrides[get_reader] = override_get_reader
app.dependency_overrides[get_embedding_service] = override_get_embedding_service
app.dependency_overrides[get_llm] = override_get_llm
app.dependency_overrides[get_writer] = override_get_writer


class TestLLMRoute(unittest.TestCase):

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
        resp = client.post("/llm", json=self.question)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"], "GDS is cool.")