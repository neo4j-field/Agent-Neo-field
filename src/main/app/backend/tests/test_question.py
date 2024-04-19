import unittest

from objects.question import Question

class TestQuestion(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_init(self) -> None:
        Question(session_id="s-123", 
                 conversation_id="conv-123", 
                 question="This is the content.", 
                 conversation_history="this is some history.",
                 message_history=["user-123", "llm-123", "user-456", "llm-456"],
                 llm_type="gpt-4 8k",
                 number_of_documents=5, 
                 temperature=0.7)
        Question(session_id="s-123", 
                 conversation_id="conv-123", 
                 question="This is the content.", 
                 llm_type="GPT-4 32k",
                 number_of_documents=5, 
                 temperature=0.7)

    def test_bad_init(self) -> None:
        with self.assertRaises(ValueError):
                Question(session_id="conv-123", 
                    conversation_id="conv-123", 
                    question="This is the content.", 
                    conversation_history="this is some history.",
                    message_history=["user-123", "llm-123", "user-456", "llm-456"],
                    llm_type="gpt-4 8k",
                    number_of_documents=5, 
                    temperature=0.7)
        with self.assertRaises(ValueError):
                Question(session_id="s-123", 
                    conversation_id="s-123", 
                    question="This is the content.", 
                    conversation_history="this is some history.",
                    message_history=["user-123", "llm-123", "user-456", "llm-456"],
                    llm_type="gpt-4 8k",
                    number_of_documents=5, 
                    temperature=0.7)
        with self.assertRaises(ValueError):
                Question(session_id="s-123", 
                    conversation_id="conv-123", 
                    question="", 
                    conversation_history=123,
                    message_history=["user-123", "llm-123", "user-456", "llm-456"],
                    llm_type="gpt-4 8k",
                    number_of_documents=5, 
                    temperature=0.7)
        with self.assertRaises(ValueError):
                Question(session_id="s-123", 
                    conversation_id="conv-123", 
                    question="This is the content.", 
                    conversation_history="this is some history.",
                    message_history=["llm-456"],
                    llm_type="gpt-4 8k",
                    number_of_documents=5, 
                    temperature=0.7)
        with self.assertRaises(ValueError):
                Question(session_id="s-123", 
                    conversation_id="conv-123", 
                    question="This is the content.", 
                    conversation_history="this is some history.",
                    message_history=["user-123", "llm-123", "user-456", "llm-456"],
                    llm_type="gpt-5",
                    number_of_documents=5, 
                    temperature=0.7)
        with self.assertRaises(ValueError):
                Question(session_id="s-123", 
                    conversation_id="conv-123", 
                    question="This is the content.", 
                    conversation_history="this is some history.",
                    message_history=["user-123", "llm-123", "user-456", "llm-456"],
                    llm_type="gpt-4 8k",
                    number_of_documents=11, 
                    temperature=0.7)
        with self.assertRaises(ValueError):
                Question(session_id="s-123", 
                    conversation_id="conv-123", 
                    question="This is the content.", 
                    conversation_history="this is some history.",
                    message_history=["user-123", "llm-123", "user-456", "llm-456"],
                    llm_type="gpt-4 8k",
                    number_of_documents=5, 
                    temperature=2)