import unittest

from objects.response import Response

class TestResponse(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_init(self) -> None:
        Response(session_id="s-123", conversation_id="conv-123", content="This is the content.", message_history=["user-123", "llm-123", "user-456", "llm-456"])

    def test_bad_init(self) -> None:
        with self.assertRaises(ValueError):
            Response(session_id="conv-123", conversation_id="conv-123", content="This is the content.", message_history=["user-123", "llm-123", "user-456", "llm-456"])
        with self.assertRaises(ValueError):
            Response(session_id="s-123", conversation_id="s-123", content="This is the content.", message_history=["user-123", "llm-123", "user-456", "llm-456"])
        with self.assertRaises(ValueError):
            Response(session_id="s-123", conversation_id="conv-123", content=123, message_history=["user-123", "llm-123", "user-456", "llm-456"])
        with self.assertRaises(ValueError):
            Response(session_id="s-123", conversation_id="conv-123", content="This is the content.", message_history=[])
        with self.assertRaises(ValueError):
            Response(session_id="s-123", conversation_id="conv-123", content="This is the content.", message_history=["llm-123"])
        with self.assertRaises(ValueError):
            Response(session_id="s-123", conversation_id="conv-123", content="This is the content.", message_history=["user-123", "user-456"])
        with self.assertRaises(ValueError):
            Response(session_id="s-123", conversation_id="conv-123", content="This is the content.", message_history=["user-123", "llm-123", "llm-135", "llm-456"])




