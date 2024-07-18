import unittest

from objects.graphtypes import AssistantMessage
from resources.prompts.prompts import prompt_no_context_template, prompt_template


class TestAssistantMessage(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_init(self) -> None:
        AssistantMessage(
            session_id="s-123",
            conversation_id="conv-123",
            prompt=prompt_template,
            content="this is content.",
            number_of_documents=10,
            temperature=0.55,
            public=True,
        )
        AssistantMessage(
            session_id="s-123",
            conversation_id="conv-123",
            prompt=prompt_no_context_template,
            content="this is content.",
            number_of_documents=10,
            temperature=0.0,
            public=True,
            vector_index_search=False,
        )

    def test_bad_session_id(self) -> None:
        with self.assertRaises(ValueError):
            AssistantMessage(
                session_id="conv-123",
                conversation_id="conv-123",
                prompt=prompt_template,
                content="this is content.",
                number_of_documents=10,
                temperature=0.0,
                public=True,
                vector_index_search=False,
            )

    def test_bad_conversation_id(self) -> None:
        with self.assertRaises(ValueError):
            AssistantMessage(
                session_id="s-123",
                conversation_id="s-123",
                prompt=prompt_template,
                content="this is content.",
                number_of_documents=10,
                temperature=0.0,
                public=True,
                vector_index_search=False,
            )

    def test_bad_content(self) -> None:
        with self.assertRaises(ValueError):
            AssistantMessage(
                session_id="s-123",
                conversation_id="conv-123",
                prompt=prompt_template,
                content="",
                number_of_documents=10,
                temperature=0.0,
                public=True,
                vector_index_search=False,
            )

    def test_bad_prompt(self) -> None:
        with self.assertRaises(ValueError):
            AssistantMessage(
                session_id="s-123",
                conversation_id="conv-123",
                prompt="bad prompt",
                content="this is content.",
                number_of_documents=10,
                temperature=0.0,
                public=True,
                vector_index_search=False,
            )

    def test_bad_message_id(self) -> None:
        with self.assertRaises(ValueError):
            AssistantMessage(
                session_id="s-123",
                conversation_id="conv-123",
                message_id="user-123",
                prompt=prompt_template,
                content="this is content.",
                number_of_documents=10,
                temperature=0.0,
                public=True,
                vector_index_search=False,
            )

    def test_documents_number(self) -> None:
        with self.assertRaises(ValueError):
            AssistantMessage(
                session_id="s-123",
                conversation_id="conv-123",
                prompt=prompt_template,
                content="this is content.",
                number_of_documents=11,
                temperature=0.0,
                public=True,
                vector_index_search=False,
            )

    def test_bad_temperature(self) -> None:
        with self.assertRaises(ValueError):
            AssistantMessage(
                session_id="s-123",
                conversation_id="conv-123",
                prompt=prompt_template,
                content="this is content.",
                number_of_documents=10,
                temperature=2,
                public=True,
                vector_index_search=False,
            )
