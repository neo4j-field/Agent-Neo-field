import unittest

import pandas as pd

from tools.llm import LLM
from resources.prompts.prompts import prompt_no_context_template, prompt_template


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
        question = "What is GDS?"

        truth_with_context = prompt_template.format(
            question=question, context=context_df.to_dict("records")
        )
        truth_without_context = prompt_no_context_template.format(question=question)

        self.assertEqual(
            llm._format_llm_input(question=question, context=context_df),
            truth_with_context,
        )
        self.assertEqual(
            llm._format_llm_input(question=question), truth_without_context
        )
