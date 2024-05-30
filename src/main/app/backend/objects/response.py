from typing import List

from pydantic import BaseModel, Field, field_validator


class Response(BaseModel):
    """
    Contains the LLM response and associated IDs.
    """

    session_id: str = Field(pattern=r"^s-.*", description="The session ID.")
    conversation_id: str = Field(
        pattern=r"^conv-.*", description="The conversation ID."
    )
    content: str = Field(description="The generated response message from the LLM.")
    message_history: List[str] = Field(
        min_length=2,
        description="A sequential list of the message ID history for a conversation.",
    )

    @field_validator("message_history")
    def validate_message_history(cls, v: List[str]) -> List[str]:
        for i in range(len(v)):
            if i % 2 == 0:
                assert v[i].startswith("user-")
            else:
                assert v[i].startswith("llm-")
        return v
