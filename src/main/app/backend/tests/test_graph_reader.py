import os
import unittest
from typing import ClassVar

from database.communicator import GraphReader
from tools.embedding import FakeEmbeddingService
from tools.secret_manager import SecretManager


class TestGraphReader(unittest.TestCase):
    sm: ClassVar[SecretManager]
    gr: ClassVar[GraphReader]
    embedder: ClassVar[FakeEmbeddingService]

    @classmethod
    def setUpClass(cls) -> None:
        assert (
            os.environ.get("DATABASE_TYPE") == "dev"
        ), f"Current db is {os.environ.get('DATABASE_TYPE')}. Please change to dev for testing."
        cls.sm = SecretManager.from_auto()
        cls.gr = GraphReader(secret_manager=cls.sm)
        cls.embedder = FakeEmbeddingService(embedding_length=768)

    def test_standard_context_retrieval(self) -> None:
        context = TestGraphReader.gr.retrieve_context_documents(
            question_embedding=TestGraphReader.embedder.get_embedding("What is gds?"),
            number_of_context_documents=5,
        )
        self.assertEqual(len(context), 5)

        context = TestGraphReader.gr.retrieve_context_documents(
            question_embedding=TestGraphReader.embedder.get_embedding("What is gds?")
        )
        self.assertEqual(len(context), 10)

        TestGraphReader.gr.close_driver()

    def test_match_by_id(self) -> None:
        ids = [
            "conv-20aa11bb-d65b-4c77-a6f3-58a39d8d0205",
            "conv-692266c4-33ba-4f6f-bf41-fcea75fd2579",
        ]
        num_nodes = TestGraphReader.gr.match_by_id(ids=ids)
        TestGraphReader.gr.close_driver()

        self.assertEqual(num_nodes, len(ids))
