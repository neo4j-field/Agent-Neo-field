from typing import List

from pydantic import BaseModel


class Response(BaseModel):
    """
    Contains the LLM response and associated IDs.
    """

    session_id: str
    conversation_id: str
    content: str
    message_history: List[str]
    
    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)