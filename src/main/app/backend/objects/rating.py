from typing import List, Dict, Union

from pydantic import BaseModel


class Rating(BaseModel):
    """
    Contains the message rating input from the frontend.
    """

    session_id: str
    conversation_id: str
    message_id: str
    value: str
    message: str = ""

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)

        self._assert_proper_ids()
        self._assert_proper_rating()
    
    def _assert_proper_ids(self) -> None:
        """
        Validate the ID prefixes.
        """

        if not self.session_id.startswith("s-"):
            raise ValueError("Invalid session_id prefix. Must start with s-")
        if not self.conversation_id.startswith("conv-"):
            raise ValueError("Invalid conversation_id prefix. Must start with conv-")
        if not self.message_id.startswith("llm-"):
            raise ValueError("Invalid message_id prefix. Must start with llm-")
    
    def _assert_proper_rating(self) -> None:
        """
        Validate the rating value.
        """

        if self.value not in ["Good", "Bad"]:
            raise ValueError("Invalid rating given. Must be either 'Good' or 'Bad'.")