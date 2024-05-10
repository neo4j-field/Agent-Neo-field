import os
from typing import List, Dict, Union, Tuple
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends

from database.communicator import GraphReader, GraphWriter
from objects.question import Question
from objects.response import Response
from objects.nodes import UserMessage, AssistantMessage
from resources.prompts.prompts import prompt_no_context_template, prompt_template
from tools.embedding import TextEmbeddingService, EmbeddingServiceProtocol
from tools.llm import LLM
from tools.secret_manager import SecretManager

PUBLIC = True

sm = SecretManager()
router = APIRouter()


def get_reader():
    reader = GraphReader(secret_manager=sm)
    try:
        yield reader
    finally:
        reader.close_driver()


def get_writer():
    writer = GraphWriter(secret_manager=sm)
    try:
        yield writer
    finally:
        writer.close_driver()


def get_embedding_service() -> EmbeddingServiceProtocol:
    return TextEmbeddingService()


def get_llm(question: Question) -> LLM:
    return LLM(llm_type=question.llm_type, temperature=question.temperature)


@router.get("/")
def get_default() -> str:
    return "Agent Neo backend is live."


# Todo: Implement bearer tokens in the backend?
# right now anyone with the url and the endpoints can hit them
@router.post("/llm_dummy", response_model=Response)
async def get_response(question: Question) -> Response:
    """
    Dummy test.
    """

    question_embedding = [0.321, 0.123]
    llm_response = "This call works!"

    user_message = UserMessage(
        session_id=question.session_id,
        conversation_id=question.conversation_id,
        content=question.question,
        embedding=question_embedding,
        public=PUBLIC,
    )

    assistant_message = AssistantMessage(
        session_id=question.session_id,
        conversation_id=question.conversation_id,
        prompt=prompt_no_context_template,
        content=llm_response,
        public=PUBLIC,
        vectorIndexSearch=True,
        number_of_documents=question.number_of_documents,
        temperature=question.temperature,
    )

    return Response(
        session_id=question.session_id,
        conversation_id=question.conversation_id,
        content=llm_response,
        message_history=question.message_history
        + [user_message.message_id, assistant_message.message_id],
    )


@router.post("/llm", response_model=Response)
async def get_response(
    question: Question,
    background_tasks: BackgroundTasks,
    reader: GraphReader = Depends(get_reader),
    writer: GraphWriter = Depends(get_writer),
    embedding_service: EmbeddingServiceProtocol = Depends(get_embedding_service),
    llm: LLM = Depends(get_llm),
) -> Response:
    """
    Gather context from the graph and retrieve a response from the designated LLM endpoint.
    """

    question_embedding = embedding_service.get_embedding(text=question.question)
    print("got embedding...")
    context = reader.retrieve_context_documents(
        question_embedding=question_embedding,
        number_of_context_documents=question.number_of_documents,
    )
    # print(context)
    print("context retrieved...")
    # llm = LLM(llm_type=question.llm_type, temperature=question.temperature)
    print("llm initialized...")
    user_id: str = "user-" + str(uuid4())
    assistant_id: str = "llm-" + str(uuid4())
    llm_response = llm.get_response(
        question=question, context=context, user_id=user_id, assistant_id=assistant_id
    )
    print("response retrieved...")
    print(llm_response)
    user_message = UserMessage(
        session_id=question.session_id,
        conversation_id=question.conversation_id,
        message_id=user_id,
        content=question.question,
        embedding=question_embedding,
        public=PUBLIC,
    )

    assistant_message = AssistantMessage(
        session_id=question.session_id,
        conversation_id=question.conversation_id,
        message_id=assistant_id,
        prompt=get_prompt(context=context),
        content=llm_response.content,
        public=PUBLIC,
        vector_index_search=True,
        number_of_documents=question.number_of_documents,
        temperature=question.temperature,
    )

    background_tasks.add_task(
        log_user_message,
        user_message,
        question.message_history,
        question.llm_type,
        question.temperature,
        writer,
    )
    background_tasks.add_task(
        log_assistant_message,
        assistant_message,
        user_message.message_id,
        list(context["index"]),
        writer,
    )
    print("returning...")
    return Response(
        session_id=question.session_id,
        conversation_id=question.conversation_id,
        content=llm_response.content,
        message_history=question.message_history
        + [user_message.message_id, assistant_message.message_id],
    )


def log_user_message(
    message: UserMessage,
    message_history: List[str],
    llm_type: str,
    temperature: float,
    writer: GraphWriter,
) -> None:
    """
    Log a user message in the graph. If this is the first message, then also log the conversation and session.
    """

    if len(message_history) == 0:
        writer.log_new_conversation(
            message=message, llm_type=llm_type, temperature=temperature
        )

    else:
        writer.log_user(message=message, previous_message_id=message_history[-1])


def log_assistant_message(
    message: AssistantMessage,
    previous_message_id: str,
    context_ids: List[str],
    writer: GraphWriter,
) -> None:
    """
    Log an assistant message in the graph.
    """

    writer.log_assistant(
        message=message,
        previous_message_id=previous_message_id,
        context_ids=context_ids,
    )


def get_prompt(context: List[str]) -> str:
    """
    Determine the prompt used for LLM query.
    """

    return prompt_no_context_template if len(context) < 1 else prompt_template
