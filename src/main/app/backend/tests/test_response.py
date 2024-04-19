import unittest

from objects.response import Response

class TestResponse(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_init(self) -> None:
        Response(session_id="s-123", conversation_id="conv-123", content="This is the content.", message_history=["user-123", "llm-123", "user-456", "llm-456"])

    def test_bad_session_id(self) -> None:
        with self.assertRaises(ValueError):
            Response(session_id="conv-123", conversation_id="conv-123", content="This is the content.", message_history=["user-123", "llm-123", "user-456", "llm-456"])
    def test_bad_conversation_id(self) -> None:
        with self.assertRaises(ValueError):
            Response(session_id="s-123", conversation_id="s-123", content="This is the content.", message_history=["user-123", "llm-123", "user-456", "llm-456"])
    def test_bad_content(self) -> None:   
        with self.assertRaises(ValueError):
            Response(session_id="s-123", conversation_id="conv-123", content=123, message_history=["user-123", "llm-123", "user-456", "llm-456"])
    def test_bad_message_history_empty(self) -> None:    
        with self.assertRaises(ValueError):
            Response(session_id="s-123", conversation_id="conv-123", content="This is the content.", message_history=[])
    def test_bad_message_history_missing_user(self) -> None:    
        with self.assertRaises(ValueError):
            Response(session_id="s-123", conversation_id="conv-123", content="This is the content.", message_history=["llm-123"])
    def test_bad_message_history_missing_llm(self) -> None:    
        with self.assertRaises(ValueError):
            Response(session_id="s-123", conversation_id="conv-123", content="This is the content.", message_history=["user-123", "user-456"])
    def test_bad_message_history_multiple_skipped(self) -> None:    
        with self.assertRaises(ValueError):
            Response(session_id="s-123", conversation_id="conv-123", content="This is the content.", message_history=["user-123", "llm-123", "llm-135", "llm-456"])




