import unittest

from objects.nodes import UserMessage


class TestUserMessage(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_init(self) -> None:
        UserMessage(
            session_id="s-123",
            conversation_id="conv-123",
            content="this is content.",
            embedding=[0.123, 0.543],
            public=True,
            role="user",
        )
        UserMessage(
            session_id="s-123",
            conversation_id="conv-123",
            content="this is content.",
            embedding=[0.123, 0.543],
            public=False,
        )

    def test_bad_session_id(self) -> None:
        with self.assertRaises(ValueError):
            UserMessage(
                session_id="conv-123",
                conversation_id="conv-123",
                content="this is content.",
                embedding=[0.123, 0.543],
                public=True,
            )

    def test_bad_conversation_id(self) -> None:
        with self.assertRaises(ValueError):
            UserMessage(
                session_id="s-123",
                conversation_id="s-123",
                content="this is content.",
                embedding=[0.123, 0.543],
                public=True,
            )

    def test_bad_content(self) -> None:
        with self.assertRaises(ValueError):
            UserMessage(
                session_id="s-123",
                conversation_id="conv-123",
                content="",
                embedding=[0.123, 0.543],
                public=True,
            )

    def test_bad_embedding(self) -> None:
        with self.assertRaises(ValueError):
            UserMessage(
                session_id="s-123",
                conversation_id="conv-123",
                content="this is content.",
                public=True,
            )

    def test_bad_message_id(self) -> None:
        with self.assertRaises(ValueError):
            UserMessage(
                session_id="s-123",
                conversation_id="conv-123",
                message_id="llm-123",
                content="this is content.",
                embedding=[0.123, 0.543],
                public=True,
            )

    def test_bad_role(self) -> None:
        with self.assertRaises(ValueError):
            UserMessage(
                session_id="s-123",
                conversation_id="conv-123",
                message_id="llm-123",
                content="this is content.",
                embedding=[0.123, 0.543],
                public=True,
                role="assistant",
            )
