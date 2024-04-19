from typing import List, Dict, Union

from pydantic import BaseModel, Field, field_validator

VALID_MODELS: List[str] = ["chat-bison 2k", "chat-bison 32k", "gemini", "gpt-4 8k", "gpt-4 32k"]

class Question(BaseModel):
    """
    Contains the user input from the frontend.
    """

    session_id: str = Field(pattern=r'^s-.*', description="The session ID.")
    conversation_id: str = Field(pattern=r'^conv-.*', description="The conversation ID.")
    question: str = Field(description="The generated response message from the LLM.")
    message_history: List[str] = Field(default=[], min_length=0, description="A sequential list of the message ID history for a conversation.")
    conversation_history: str = Field(default="", description="A summary of the conversation so far.")
    llm_type: str = Field(description="The LLM to use for response generation.")
    number_of_documents: int = Field(default=10, ge=0, le=10, description="The number of documents to use as context.")
    temperature: float = Field(default=0.0, ge=0.0, le=1.0, description="Temperature parameter for the LLM.")
    
    @field_validator("message_history")
    def validate_message_history(cls, v: List[str]) -> List[str]:
        for i in range(len(v)):
            if i % 2 == 0:
                assert v[i].startswith("user-")
            else:
                assert v[i].startswith("llm-")
        return v
    
    @field_validator("llm_type")
    def validate_llm_type(cls, v: str) -> str:
        if v.lower() not in VALID_MODELS:
            raise ValueError(f"llm_type must be one of the following: {str(VALID_MODELS)}.")
        return v.lower()