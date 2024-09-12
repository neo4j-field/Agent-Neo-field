from functools import cached_property
from typing import Optional

import pandas as pd
from langchain_community.chat_models import ChatOpenAI, FakeListChatModel
from langchain_google_vertexai import ChatVertexAI
from objects.question import Question
from pydantic import BaseModel, Field, validator
from resources.prompts import (get_prompt_no_context_template,
                               get_prompt_template)
from resources.valid_models import get_valid_models
from tools.secret_manager import EnvSecretManager

sm = EnvSecretManager(env_path=".env")


class LLM(BaseModel):
    """
    Interface for interacting with different LLMs.
    """

    llm_type: str = Field(description="The llm type to use in the conversation.")
    temperature: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Temperature parameter for the LLM."
    )

    @validator("llm_type")
    def validate_llm_type(cls, v: str) -> str:
        if v.lower() not in get_valid_models() + ["fake"]:
            raise ValueError(
                f"llm_type must be one of the following: {str(get_valid_models())}."
            )
        return v.lower()

    @validator("temperature")
    def validate_temperature(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Temperature must be between 0.0 and 1.0.")
        return v

    @cached_property
    def llm_instance(self) -> ChatVertexAI | ChatOpenAI | FakeListChatModel:
        return self._init_llm()

    def _init_llm(self):
        """
        This function initializes an LLM for conversation.
        Each time the LLM type is changed, the conversation is reinitialized
        and history is lost.
        """

        match self.llm_type:
            case "fake":
                return FakeListChatModel(responses=["GDS is cool."])
            case "chat-bison 2k":
                return ChatVertexAI(
                    model_name="chat-bison",
                    max_output_tokens=1024,  # this is the max allowed
                    temperature=self.temperature,  # default temp is 0.0
                    top_p=0.95,  # default is 0.95
                    top_k=40,  # default is 40
                )
            case "chat-bison 32k":
                return ChatVertexAI(
                    model_name="chat-bison-32k",
                    max_output_tokens=8192,  # this is the max allowed
                    temperature=self.temperature,  # default temp is 0.0
                    top_p=0.95,  # default is 0.95
                    top_k=40,  # default is 40
                )
            case "gemini":
                return ChatVertexAI(model_name="gemini-pro")
            case "gpt-4 8k":
                # Tokens per Minute Rate Limit (thousands): 10
                # Rate limit (Tokens per minute): 10000
                # Rate limit (Requests per minute): 60
                return ChatOpenAI(
                    model="gpt-4",
                    api_key=sm.access_secret_version("OPENAI_API_KEY"),
                    temperature=self.temperature,
                )  # default is 0.7
                # return OpenAI(api_key=sm.access_secret_version("openai_key_dan"),
                #                            model="gpt-4",
                #                            temperature=temperature)
            case "gpt-4 32k":
                # Tokens per Minute Rate Limit (thousands): 30
                # Rate limit (Tokens per minute): 30000
                # Rate limit (Requests per minute): 180
                return ChatOpenAI(
                    model_name="gpt-4-turbo",
                    api_key=sm.access_secret_version("OPENAI_API_KEY"),
                    temperature=self.temperature,
                )  # default is 0.7
                # return OpenAI(api_key=sm.access_secret_version("openai_key_dan"),
                #                            model="gpt-4-32k",
                #                            temperature=temperature)
            case _:
                raise ValueError("Please provide a valid LLM type.")

    def get_response(
        self,
        question: Question,
        user_id: str,
        assistant_id: str,
        context: Optional[pd.DataFrame] = None,
    ) -> str:
        """
        Get a response from the LLM.
        """

        llm_input = self._format_llm_input(question=question, context=context)

        # return self.llm_instance.predict(llm_input)
        return self.llm_instance.invoke(
            llm_input,
            {
                "metadata": {
                    "conversation_id": question.conversation_id,
                    "session_id": question.session_id,
                    "user_id": user_id,
                    "assistant_id": assistant_id,
                }
            },
        )

    def _format_llm_input(
        self, question: Question, context: Optional[pd.DataFrame] = None
    ) -> str:
        if context is not None and isinstance(context, pd.DataFrame):
            return get_prompt_template(
                question=question, context=context[["url", "text"]]
            )
        else:
            return get_prompt_no_context_template(question=question)
