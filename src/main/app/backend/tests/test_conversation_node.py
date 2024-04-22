import unittest

from objects.nodes import Conversation


class TestConversation(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_init(self) -> None:
        Conversation(
            session_id="s-123", conversation_id="conv-123", llm_type="gpt-4 32k"
        )

    def test_bad_conversation_id(self) -> None:
        with self.assertRaises(ValueError):
            Conversation(
                session_id="s-123", conversation_id="s-123", llm_type="gpt-4 32k"
            )

    def test_bad_session_id(self) -> None:
        with self.assertRaises(ValueError):
            Conversation(
                session_id="conv-123", conversation_id="conv-123", llm_type="gpt-4 32k"
            )

    def test_bad_llm_type(self) -> None:
        with self.assertRaises(ValueError):
            Conversation(
                session_id="s-123", conversation_id="conv-123", llm_type="llama2"
            )
