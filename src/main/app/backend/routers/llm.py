from typing import List
from uuid import uuid4
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from database.communicator import GraphWriter, GraphReader
from objects.question import Question
from objects.response import Response, GraphResponse
from objects.graphtypes import (UserMessage, AssistantMessage, ConversationEntry, MessageNode, DocumentNode,
                                DocumentRelationship, MessageRelationship)
from resources.prompts import get_prompt_no_context_template, get_prompt_template, get_prompt_no_context
from tools.embedding import TextEmbeddingService, EmbeddingServiceProtocol
from tools.llm import LLM
from tools.secret_manager import SecretManager, GoogleSecretManager, EnvSecretManager

PUBLIC = True

secret_manager = EnvSecretManager(env_path='.env')
router = APIRouter()


def get_prompt(context: List[str]) -> str:
    """
    Determine the prompt used for LLM query.
    """
    return get_prompt_no_context_template() if len(context) < 1 else get_prompt_template()


def get_reader():
    reader = GraphReader(secret_manager=secret_manager)
    try:
        yield reader
    finally:
        reader.close_driver()


def get_writer():
    writer = GraphWriter(secret_manager=secret_manager)
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
    no_context_prompt = get_prompt_no_context()

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
        prompt=no_context_prompt,
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

    user_id: str = "user-" + str(uuid4())
    assistant_id: str = "llm-" + str(uuid4())
    llm_response = llm.get_response(question=question, context=context, user_id=user_id, assistant_id=assistant_id)
    print("response retrieved...")
    print(llm_response)
    user_message = UserMessage(session_id=question.session_id,
                               conversation_id=question.conversation_id,
                               message_id=user_id,
                               content=question.question,
                               embedding=question_embedding,
                               public=PUBLIC)

    assistant_message = AssistantMessage(session_id=question.session_id,
                                         conversation_id=question.conversation_id,
                                         message_id=assistant_id,
                                         prompt=get_prompt(context=context),
                                         content=llm_response.content,
                                         public=PUBLIC,
                                         vectorIndexSearch=True,
                                         number_of_documents=question.number_of_documents,
                                         temperature=question.temperature)

    background_tasks.add_task(log_user_message,
                              user_message,
                              question.message_history, question.llm_type,
                              question.temperature,
                              writer
                              )

    background_tasks.add_task(log_assistant_message,
                              assistant_message,
                              user_message.message_id,
                              list(context['index']),
                              writer
                              )
    print("returning...")
    return Response(session_id=question.session_id,
                    conversation_id=question.conversation_id,
                    content=llm_response.content,
                    message_history=question.message_history + [user_message.message_id, assistant_message.message_id],
                    graph_data=context)


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


@router.get("/graph-llm/{conversation_id}", response_model=GraphResponse)
async def get_graph_response(conversation_id: str, reader: GraphReader = Depends(get_reader)):
    """
    Endpoint to fetch detailed graph data and conversation history for a given conversation ID.
    """
    try:
        history_data = reader.retrieve_conversation_history(conversation_id)

        if not history_data:
            raise HTTPException(status_code=404, detail="Conversation not found")

        conversation_entries = []

        for messages, documents in history_data:
            message_nodes, message_rels = messages
            document_nodes, document_rels = documents

            entry = ConversationEntry(
                document_nodes=[create_document_node(doc) for doc in document_nodes],
                message_nodes=[create_message_node(msg) for msg in message_nodes],
                document_relationships=[create_document_relationship(rel) for rel in document_rels],
                message_relationships=[create_message_relationship(rel) for rel in message_rels]
            )

            conversation_entries.append(entry)

        return GraphResponse(conversation_entries=conversation_entries)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def create_document_node(data: dict) -> DocumentNode:
    required_fields = ["community", "contextCount", "embedding", "fast_rp_similarity", "index", "pageRank", "text",
                       "url"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        raise ValueError(f"Missing fields: {missing_fields}")

    return DocumentNode(**data)


def create_message_node(data: dict) -> MessageNode:
    required_fields = ["id", "content", "role", "postTime"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        raise ValueError(f"Missing fields: {missing_fields}")

    return MessageNode(**data)


def create_document_relationship(data: dict) -> DocumentRelationship:
    required_fields = ["start_node", "end_node"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        raise ValueError(f"Missing fields: {missing_fields}")

    return DocumentRelationship(
        start_node=create_document_node(data['start_node']),
        end_node=create_document_node(data['end_node'])
    )


def create_message_relationship(data: dict) -> MessageRelationship:
    required_fields = ["start_node", "end_node"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        raise ValueError(f"Missing fields: {missing_fields}")

    return MessageRelationship(
        start_node=create_message_node(data['start_node']),
        end_node=create_message_node(data['end_node'])
    )
