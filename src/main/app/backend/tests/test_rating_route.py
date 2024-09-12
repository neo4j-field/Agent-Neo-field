import unittest

from fastapi.testclient import TestClient
from routers.llm import get_writer
from tests.test_llm_route import GraphWriterMock

from main import app

client = TestClient(app)


def override_get_writer():
    return GraphWriterMock()


app.dependency_overrides[get_writer] = override_get_writer


class TestRatingRoute(unittest.TestCase):
    rating: dict[str, str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.rating = {
            "session_id": "s-123-test",
            "conversation_id": "conv-123-test",
            "message_id": "llm-123-test",
            "value": "Good",
            "message": "good job",
        }

    def test_rating_route(self) -> None:
        resp = client.post("/rating", json=self.rating)
        self.assertEqual(resp.status_code, 200)
