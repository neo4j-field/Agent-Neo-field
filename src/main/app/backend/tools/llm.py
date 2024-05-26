import os
from typing import List, Dict, Tuple

import openai
from langchain_community.chat_models import AzureChatOpenAI
from langchain_core.messages import BaseMessage
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_vertexai import ChatVertexAI
from langchain_openai import OpenAI
# from langchain.chains import ConversationChain
import pandas as pd
from pydantic import BaseModel

from objects.question import Question
from resources.prompts import get_prompt_template, get_prompt_no_context_template
from tools.secret_manager import EnvSecretManager

sm = EnvSecretManager(env_path='.env')
#os.environ["LANGCHAIN_API_KEY"] = sm.access_secret_version("LANGSMITH_API_KEY")

class LLM(BaseModel):
    """
    Interface for interacting with different LLMs.
    """

    llm_type: str
    temperature: float = 0.7
    llm_instance: ChatVertexAI | AzureChatOpenAI | None = None

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)

        self._init_llm(llm_type=self.llm_type, temperature=self.temperature)
        
    def _init_llm(self, llm_type: str, temperature: float):
        """
        This function initializes an LLM for conversation.
        Each time the LLM type is changed, the conversation is reinitialized
        and history is lost.
        """

        match llm_type:
            case "chat-bison 2k":
                self.llm_instance = ChatVertexAI(model_name='chat-bison',
                        max_output_tokens=1024, # this is the max allowed
                        temperature=temperature, # default temp is 0.0
                        top_p=0.95, # default is 0.95
                        top_k = 40 # default is 40
                       )
            case "chat-bison 32k":
                self.llm_instance = ChatVertexAI(model_name='chat-bison-32k',
                        max_output_tokens=8192, # this is the max allowed 
                        temperature=temperature, # default temp is 0.0
                        top_p=0.95, # default is 0.95
                        top_k = 40 # default is 40
                       )
            case "Gemini":
                self.llm_instance = ChatVertexAI(model_name="gemini-pro")
            case "GPT-4 8k":
                # Tokens per Minute Rate Limit (thousands): 10
                # Rate limit (Tokens per minute): 10000
                # Rate limit (Requests per minute): 60
                self.llm_instance = AzureChatOpenAI(openai_api_version=openai.api_version,
                       openai_api_key = openai.api_key,
                       openai_api_base = sm.access_secret_version('openai_endpoint'),
                       deployment_name = sm.access_secret_version('gpt4_8k_name'),
                       model_name = 'gpt-4',
                       temperature=temperature) # default is 0.7
                # self.llm_instance = OpenAI(api_key=sm.access_secret_version("openai_key_dan"),
                #                            model="gpt-4",
                #                            temperature=temperature)
            case "GPT-4 32k":
                # Tokens per Minute Rate Limit (thousands): 30
                # Rate limit (Tokens per minute): 30000
                # Rate limit (Requests per minute): 180
                self.llm_instance = AzureChatOpenAI(openai_api_version=openai.api_version,
                       openai_api_key = openai.api_key,
                       openai_api_base = sm.access_secret_version('openai_endpoint'),
                       deployment_name = sm.access_secret_version('gpt4_32k_name'),
                       model_name = 'gpt-4-32k',
                       temperature=temperature) # default is 0.7
                # self.llm_instance = OpenAI(api_key=sm.access_secret_version("openai_key_dan"),
                #                            model="gpt-4-32k",
                #                            temperature=temperature)
            case _:
                raise ValueError("Please provide a valid LLM type.")
    
    def _format_llm_input(self, question: str, context: pd.DataFrame | None = None) -> str:
        """
        Format the LLM input and return the input along with the context IDs if they exist.
        """

        if context is not None:
            print("creating context prompt...")
            return get_prompt_template(question=question, context=context[['url', 'text']].to_dict('records'))
        else:
            print("creating non-context prompt...")
            return get_prompt_no_context_template(question=question)
                    
    def get_response(self, question: Question, user_id: str, assistant_id: str, context: pd.DataFrame | None = None) -> BaseMessage:
        """
        Get a response from the LLM.
        """

        llm_input = self._format_llm_input(question=question.question, context=context)

        print("llm input: ", llm_input)
        # return self.llm_instance.predict(llm_input)
        return self.llm_instance.invoke(llm_input, {"metadata": {"conversation_id": question.conversation_id, 
                                                                 "session_id": question.session_id,
                                                                 "user_id": user_id,
                                                                 "assistant_id": assistant_id
                                                                 }
                                                    }
                                        )