import unittest

import pandas as pd
from objects.question import Question
from resources.prompts import (get_prompt_no_context_template,
                               get_prompt_template)
from tools.llm import LLM


class TestLLM(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_good_init(self) -> None:
        LLM(llm_type="gpt-4 8k", temperature=0)
        LLM(llm_type="GPT-4 8k", temperature=1)
        LLM(llm_type="gemini")

    def test_bad_llm_type(self) -> None:
        with self.assertRaises(ValueError):
            LLM(llm_type="gpt-4", temperature=0)
            LLM(llm_type="GPT-2", temperature=0)

    def test_format_llm_input(self) -> None:
        llm = LLM(llm_type="gemini")
        context_df = pd.DataFrame(
            [
                {"url": "url1", "text": "Some text for url1."},
                {"url": "url2", "text": "This is more text."},
            ]
        )
        question = Question(
            session_id="s-123-test",
            conversation_id="conv-123-test",
            question="What is GDS?",
            message_history=["user-123-test"],
            conversation_history="The user keeps asking what GDS is.",
            llm_type="GPT-4 8k",
            number_of_documents=10,
            temperature=0.7,
        )

        truth_with_context = get_prompt_template(question=question, context=context_df)
        truth_without_context = get_prompt_no_context_template(question=question)

        self.assertEqual(
            llm._format_llm_input(question=question, context=context_df),
            truth_with_context,
        )
        self.assertEqual(
            llm._format_llm_input(question=question, context=context_df),
            truth_without_context,
        )
