import os
import unittest

from langchain_community.embeddings import FakeEmbeddings
from database.communicator import GraphReader
from tools.secret_manager import SecretManager


class TestGraphReader(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        assert (
            os.environ.get("DATABASE_TYPE") == "dev"
        ), f"Current db is {os.environ.get('DATABASE_TYPE')}. Please change to dev for testing."
        cls.embedder = FakeEmbeddings(size=768)
        cls.sm = SecretManager()

    def test_init(self) -> None:
        gr = GraphReader(secret_manager=self.sm)
        gr.close_driver()

    def test_standard_context_retrieval(self) -> None:
        gr = GraphReader(secret_manager=self.sm)

        context = gr.retrieve_context_documents(
            question_embedding=self.embedder.embed_query("What is gds?"),
            number_of_context_documents=5,
        )
        self.assertEqual(len(context), 5)

        context = gr.retrieve_context_documents(
            question_embedding=self.embedder.embed_query("What is gds?")
        )
        self.assertEqual(len(context), 10)

        gr.close_driver()

    def test_topics_context_retrieval(self) -> None:
        # gr = GraphReader(secret_manager=self.sm)

        # context = gr.retrieve_context_documents_by_topic(
        #     question_embedding=self.embedder.embed_query("What is gds?"),
        #     number_of_topics=1,
        #     documents_per_topic=2,
        # )
        # self.assertEqual(len(context), 2)

        # context = gr.retrieve_context_documents_by_topic(
        #     question_embedding=self.embedder.embed_query("What is gds?"),
        #     number_of_topics=2,
        # )
        # self.assertEqual(len(context), 8)

        # gr.close_driver()
        pass  # not implemented

    def test_match_by_id(self) -> None:
        gr = GraphReader(secret_manager=self.sm)
        ids = [
            "conv-20aa11bb-d65b-4c77-a6f3-58a39d8d0205",
            "conv-692266c4-33ba-4f6f-bf41-fcea75fd2579",
        ]  # exist in dev database

        num_nodes = gr.match_by_id(ids=ids)
        gr.close_driver()

        self.assertEqual(num_nodes, len(ids))
