import unittest

from objects.nodes import Session

class TestSession(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_init(self) -> None:
        Session(session_id="s-123")

    def test_bad_session_id(self) -> None:
        with self.assertRaises(ValueError):
            Session(session_id="conv-123")

