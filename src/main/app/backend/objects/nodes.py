from typing import List, Dict, Union
from uuid import uuid4

from pydantic import BaseModel


class UserMessage(BaseModel):
    """
    Contains user message information.
    """

    session_id: str
    conversation_id: str
    message_id: str = "user-" + str(uuid4())
    content: str
    embedding: List[float] | None = None
    role: str = "user"
    public: bool

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)

        # self.message_id = "user-"+str(uuid4())


class AssistantMessage(BaseModel):
    """
    Contains assistant message information.
    """

    session_id: str
    conversation_id: str
    message_id: str = "llm-" + str(uuid4())
    prompt: str | None = None
    content: str
    role: str = "assistant"
    public: bool
    vectorIndexSearch: bool = True
    number_of_documents: int
    temperature: float

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)

        # self.message_id = "llm-"+str(uuid4())


class Conversation(BaseModel):
    """
    Contains conversation information.
    """

    session_id: str
    conversation_id: str
    llm_type: str

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)


class Session(BaseModel):
    """
    Contains session information.
    """

    session_id: str

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
