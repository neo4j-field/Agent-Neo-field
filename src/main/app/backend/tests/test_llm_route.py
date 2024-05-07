import unittest

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)


class TestSession(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_default(self) -> None:
        resp = client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), "Agent Neo backend is live.")