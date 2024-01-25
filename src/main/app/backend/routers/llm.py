import os
from typing import List, Dict, Union, Tuple

from fastapi import APIRouter

from database.communicator import GraphReader
from objects.question import Question
from objects.response import Response
from objects.nodes import UserMessage, AssistantMessage
from tools.embedding import TextEmbeddingService
from tools.llm import LLM

router = APIRouter()
reader = GraphReader()

@router.get("/llm_dummy", response_model=Response)
async def get_response(question: Question) -> Response:
    """
    Dummy test.
    """

    return Response(session_id=question.session_id, conversation_id=question.conversation_id, content="This call works!")

@router.get("/llm", response_model=Response)
async def get_response(question: Question) -> Response:
    """
    Gather context from the graph and retrieve a response from the designated LLM endpoint.
    """
    
    question_embedding = TextEmbeddingService().get_embedding(text=question.question)
    context = reader.retrieve_context_documents(question_embedding=question_embedding)
    print(context)

    llm = LLM(llm_type="GPT-4 8k", temperature=question.temperature)

    response = Response(session_id=question.session_id, 
                        conversation_id=question.conversation_id, 
                        content=llm.get_response(question=question.question, context=context))

    # user_message = UserMessage()
    # assistant_message = AssistantMessage()

    return response