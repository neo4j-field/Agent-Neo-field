from typing import List, Dict, Union

from pydantic import BaseModel


class Question(BaseModel):
    """
    Contains the user input from the frontend.
    """

    session_id: str
    conversation_id: str
    question: str
    conversation_history: str = ""
    message_history: List[str] | None = []
    llm_type: str
    number_of_documents: int
    temperature: float

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)

        self._assert_proper_ids()
    
    def _assert_proper_ids(self) -> None:
        """
        Validate the ID prefixes.
        """

        if not self.session_id.startswith("s-"):
            raise ValueError("Invalid session_id prefix. Must start with s-")
        if not self.conversation_id.startswith("conv-"):
            raise ValueError("Invalid conversation_id prefix. Must start with conv-")