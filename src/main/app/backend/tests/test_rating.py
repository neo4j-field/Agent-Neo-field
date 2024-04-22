import unittest

from objects.rating import Rating


class TestRating(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_init(self) -> None:
        r = Rating(
            session_id="s-123",
            conversation_id="conv-123",
            message_id="llm-123",
            value="Good",
            message="good job.",
        )
        r2 = Rating(
            session_id="s-123",
            conversation_id="conv-123",
            message_id="llm-123",
            value="Bad",
        )

    def test_bad_session_id(self) -> None:
        with self.assertRaises(ValueError):
            Rating(
                session_id="conv-123",
                conversation_id="conv-123",
                message_id="llm-123",
                value="Bad",
            )

    def test_bad_conversation_id(self) -> None:
        with self.assertRaises(ValueError):
            Rating(
                session_id="s-123",
                conversation_id="s-123",
                message_id="llm-123",
                value="Bad",
            )

    def test_bad_message_id(self) -> None:
        with self.assertRaises(ValueError):
            Rating(
                session_id="s-123",
                conversation_id="conv-123",
                message_id="user-123",
                value="Bad",
            )

    def test_bad_value(self) -> None:
        with self.assertRaises(ValueError):
            Rating(
                session_id="s-123",
                conversation_id="conv-123",
                message_id="llm-123",
                value="Meh",
            )
