import os
import time
import unittest

from dotenv import load_dotenv
from neo4j import Driver


from database.communicator import GraphWriter, GraphReader
from objects.graphtypes import UserMessage, AssistantMessage
from objects.rating import Rating
from resources.prompts.prompts import prompt_template
from tools.secret_manager import SecretManager

test_ids = {
    "session_id": "s-123-test",
    "conversation_id": "conv-123-test",
    "user_id": "user-123-test",
    "assistant_id": "llm-123-test",
    "document_id": "idx-123-test",
}


class TestGraphWriter(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        assert (
            os.environ.get("DATABASE_TYPE") == "dev"
        ), f"Current db is {os.environ.get('DATABASE_TYPE')}. Please change to dev for testing."

        cls.sm = SecretManager()
        # ensure no test data in database
        gw = GraphWriter(secret_manager=cls.sm)
        gw.delete_by_id(list(test_ids.values()))
        gw.close_driver()

    def test_init(self) -> None:
        gw = GraphWriter(secret_manager=self.sm)
        gw.close_driver()

    def test_init_via_env_variables(self) -> None:
        if not load_dotenv():
            print("No .env file loaded...")

        gw = GraphWriter()
        self.assertIsInstance(gw.driver, Driver)
        gw.close_driver()

    def test_new_conversation(self) -> None:
        gw = GraphWriter(secret_manager=self.sm)
        gr = GraphReader(secret_manager=self.sm)

        user_message = UserMessage(
            session_id=test_ids["session_id"],
            conversation_id=test_ids["conversation_id"],
            message_id=test_ids["user_id"],
            content="test content",
            embedding=[0.123, 0.456],
            public=False,
        )
        gw.log_new_conversation(
            message=user_message, llm_type="gpt-4 8k", temperature=0
        )

        num_nodes = gr.match_by_id(
            [
                test_ids["conversation_id"],
                test_ids["session_id"],
                test_ids["user_id"],
            ]
        )
        gr.close_driver()

        gw.delete_by_id(
            [
                test_ids["conversation_id"],
                test_ids["session_id"],
                test_ids["user_id"],
            ]
        )
        gw.close_driver()

        self.assertEqual(num_nodes, 3)

    def test_log_user(self) -> None:
        gw = GraphWriter(secret_manager=self.sm)
        gr = GraphReader(secret_manager=self.sm)

        gw.write_dummy_node(id=test_ids["assistant_id"], label="Message")
        user_message = UserMessage(
            session_id=test_ids["session_id"],
            conversation_id=test_ids["conversation_id"],
            message_id=test_ids["user_id"],
            content="test content",
            embedding=[0.123, 0.456],
            public=False,
        )

        gw.log_user(message=user_message, previous_message_id=test_ids["assistant_id"])

        num_nodes = gr.match_by_id([test_ids["assistant_id"], test_ids["user_id"]])
        gr.close_driver()

        gw.delete_by_id([test_ids["conversation_id"], test_ids["user_id"]])
        gw.close_driver()

        self.assertEqual(num_nodes, 2)

    def test_log_assistant(self) -> None:
        gw = GraphWriter(secret_manager=self.sm)
        gr = GraphReader(secret_manager=self.sm)

        gw.write_dummy_node(id=test_ids["user_id"], label="Message")
        gw.write_dummy_node(id=test_ids["document_id"], label="Document")
        num_nodes = gr.match_by_id([test_ids["user_id"], test_ids["document_id"]])

        assistant_message = AssistantMessage(
            session_id=test_ids["session_id"],
            conversation_id=test_ids["conversation_id"],
            message_id=test_ids["assistant_id"],
            content="test content",
            public=False,
            prompt=prompt_template,
            number_of_documents=10,
            temperature=0.5,
        )

        gw.log_assistant(
            message=assistant_message,
            previous_message_id=test_ids["user_id"],
            context_ids=[test_ids["document_id"]],
        )

        num_nodes = gr.match_by_id(
            [test_ids["user_id"], test_ids["assistant_id"], test_ids["document_id"]]
        )
        gr.close_driver()

        gw.delete_by_id(
            [test_ids["user_id"], test_ids["assistant_id"], test_ids["document_id"]]
        )
        gw.close_driver()

        self.assertEqual(num_nodes, 3)

    def test_write_dummy_node(self) -> None:
        gw = GraphWriter(secret_manager=self.sm)
        gr = GraphReader(secret_manager=self.sm)

        gw.write_dummy_node(id=test_ids["conversation_id"], label="Conversation")

        num_nodes = gr.match_by_id([test_ids["conversation_id"]])
        gr.close_driver()

        gw.delete_by_id([test_ids["conversation_id"]])
        gw.close_driver()

        self.assertEqual(num_nodes, 1)

    def test_rate_message(self) -> None:
        gw = GraphWriter(secret_manager=self.sm)
        gr = GraphReader(secret_manager=self.sm)

        gw.write_dummy_node(id=test_ids["assistant_id"], label="Message")
        r = Rating(
            session_id=test_ids["session_id"],
            conversation_id=test_ids["conversation_id"],
            message_id=test_ids["assistant_id"],
            value="Good",
            message="good job.",
        )
        gw.rate_message(r)
        r_in_graph = gr.get_message_rating(
            assistant_message_id=test_ids["assistant_id"]
        )

        self.assertEqual(r_in_graph[0], test_ids["assistant_id"])
        self.assertEqual(r_in_graph[1], r.value)
        self.assertEqual(r_in_graph[2], r.message)

        r2 = Rating(
            session_id=test_ids["session_id"],
            conversation_id=test_ids["conversation_id"],
            message_id=test_ids["assistant_id"],
            value="Bad",
        )
        gw.rate_message(r2)
        r2_in_graph = gr.get_message_rating(
            assistant_message_id=test_ids["assistant_id"]
        )

        self.assertEqual(r2_in_graph[0], test_ids["assistant_id"])
        self.assertEqual(r2_in_graph[1], r2.value)

        gw.delete_by_id([test_ids["assistant_id"]])

        gw.close_driver()
        gr.close_driver()
