from typing import List, Dict, Union

from pydantic import BaseModel, Field, field_validator


class Rating(BaseModel):
    """
    Contains the message rating input from the frontend.
    """

    session_id: str = Field(pattern=r'^s-.*', description="The session ID.")
    conversation_id: str = Field(pattern=r'^conv-.*', description="The conversation ID.")
    message_id: str = Field(pattern=r'^llm-.*', description="The LLM response message ID.")
    value: str = Field(description="Feedback must be 'Good' or 'Bad'.")
    message: str = Field(default="", description="The feedback message for a given LLM response.")
    
    @field_validator("value")
    def assert_proper_rating(cls, v: str) -> str:
        """
        Validate the rating value.
        """

        if v not in ["Good", "Bad"]:
            raise ValueError("Invalid rating given. Must be either 'Good' or 'Bad'.")
        
        return v