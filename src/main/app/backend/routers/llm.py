import os
from typing import List, Dict, Union, Tuple

from fastapi import APIRouter, BackgroundTasks

from database.communicator import GraphReader, GraphWriter
from objects.question import Question
from objects.response import Response
from objects.nodes import UserMessage, AssistantMessage
from resources.prompts.prompts import prompt_no_context_template, prompt_template
from tools.embedding import TextEmbeddingService
from tools.llm import LLM

PUBLIC=True

router = APIRouter()
reader = GraphReader()
writer = GraphWriter()

@router.post("/llm_dummy", response_model=Response)
async def get_response(question: Question, background_tasks: BackgroundTasks) -> Response:
    """
    Dummy test.
    """
    print("dummy test")
    question_embedding = [0.321, 0.123]
    llm_response = "This call works!"

    user_message = UserMessage(session_id=question.session_id,
                               conversation_id=question.conversation_id,
                               content=question.question,
                               embedding=question_embedding,
                               public=PUBLIC)
    
    assistant_message = AssistantMessage(session_id=question.session_id,
                                         conversation_id=question.conversation_id,
                                         prompt="",
                                         content=llm_response,
                                         public=PUBLIC,
                                         vectorIndexSearch=True,
                                         number_of_documents=question.number_of_documents,
                                         temperature=question.temperature)
    

    background_tasks.add_task(write_notification, question.question, message="some notification")

    
    return Response(session_id=question.session_id, 
                    conversation_id=question.conversation_id, 
                    content=llm_response, 
                    message_history=question.message_history+[user_message.message_id, assistant_message.message_id])


@router.post("/llm", response_model=Response)
async def get_response(question: Question, background_tasks: BackgroundTasks) -> Response:
    """
    Gather context from the graph and retrieve a response from the designated LLM endpoint.
    """
    
    print("real call")
    question_embedding = TextEmbeddingService().get_embedding(text=question.question)
    print("got embedding...")
    context = reader.retrieve_context_documents(question_embedding=question_embedding, number_of_context_documents=question.number_of_documents)
    # print(context)
    print("context retrieved...")
    llm = LLM(llm_type="GPT-4 8k", temperature=question.temperature)
    print("llm initialized...")
    llm_response = llm.get_response(question=question.question, context=context)
    print("response retrieved...")
    print(llm_response)
    user_message = UserMessage(session_id=question.session_id,
                               conversation_id=question.conversation_id,
                               content=question.question,
                               embedding=question_embedding,
                               public=PUBLIC)
    
    assistant_message = AssistantMessage(session_id=question.session_id,
                                         conversation_id=question.conversation_id,
                                         prompt=get_prompt(context=context),
                                         content=llm_response.content,
                                         public=PUBLIC,
                                         vectorIndexSearch=True,
                                         number_of_documents=question.number_of_documents,
                                         temperature=question.temperature)

    background_tasks.add_task(log_user_message, user_message, question.message_history, question.llm_type, question.temperature)
    background_tasks.add_task(log_assistant_message, assistant_message, user_message.message_id, list(context['index']))
    print("returning...")
    return  Response(   session_id=question.session_id, 
                        conversation_id=question.conversation_id, 
                        content=llm_response.content,
                        message_history=question.message_history+[user_message.message_id, assistant_message.message_id])

def log_user_message(message: UserMessage, message_history: List[str], llm_type: str, temperature: float) -> None:
    """
    Log a user message in the graph. If this is the first message, then also log the conversation and session.
    """

    if len(message_history) == 0:
        writer.log_new_conversation(message=message, llm_type=llm_type, temperature=temperature)

    else:
        writer.log_user(message=message, previous_message_id=message_history[-1])

def log_assistant_message(message: AssistantMessage, previous_message_id: str, context_ids: List[str]) -> None:
    """
    Log an assistant message in the graph.
    """

    writer.log_assistant(message=message, previous_message_id=previous_message_id, context_ids=context_ids)

def get_prompt(context: List[str]) -> str:
     """
     Determine the prompt used for LLM query.
     """

     return prompt_no_context_template if len(context) < 1 else prompt_template


def write_notification(email: str, message=""):
    with open("dummy_log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)