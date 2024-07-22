from typing import List
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from database.communicator import GraphWriter, GraphReader

from objects.graphtypes import (ConversationEntry, AssistantNode, MessageNode, DocumentNode, SessionNode,
                                ConversationNode,
                                MessageRelationship, ConversationRelationship, AssistantRelationship)
from objects.question import Question
from objects.response import Response, GraphResponse
from objects.types import UserMessage, AssistantMessage
from resources.prompts import get_prompt_no_context_template, get_prompt_template, get_prompt_no_context
from tools.embedding import TextEmbeddingService, EmbeddingServiceProtocol
from tools.llm import LLM
from tools.secret_manager import EnvSecretManager

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


#todo: decouple the parsing with the request.
# history_data: List[Tuple[Tuple[List, List], Tuple[List, List]]]:
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

        for documents, messages in history_data:
            message_path_nodes, message_path_rels = messages
            document_path_nodes, document_path_rels = documents

            conversation_nodes = []
            message_nodes = []
            assistant_nodes = []
            conversation_rels = []
            message_rels = []
            assistant_rels = []

            for node in message_path_nodes:
                if 'Assistant' in node.labels:
                    assistant_nodes.append(create_assistant_node(node))
                elif 'Message' in node.labels:
                    message_nodes.append(create_message_node(node))
                elif 'Conversation' in node.labels:
                    conversation_nodes.append(create_conversation_node(node))

            for rel in message_path_rels:
                start_node_labels = rel.start_node.labels
                end_node_labels = rel.end_node.labels

                if 'Message' in start_node_labels and 'Message' in end_node_labels and 'Assistant' in end_node_labels:
                    print('called here 1')
                    for k, v in rel.end_node.items():
                        print(k)
                        if k == 'id' or k == 'role':
                            print(v)
                    print(f'end node labels are: {rel.end_node.labels}')
                    data = {'start_node': rel.start_node, 'end_node': rel.end_node}
                    message_rels.append(create_message_relationship(data))
                elif 'Assistant' in start_node_labels and 'Document' in end_node_labels:
                    print('called here2')
                    data = {'start_node': rel.start_node, 'end_node': rel.end_node}
                    assistant_rels.append(create_assistant_relationship(data))
                elif 'Conversation' in start_node_labels and 'Message' in end_node_labels:
                    print('called here3')
                    data = {'start_node': rel.start_node, 'end_node': rel.end_node}
                    conversation_rels.append(create_conversation_relationship(data))

            assistant_node = create_assistant_node(document_path_nodes[0])
            document_node = create_document_node(document_path_nodes[1])
            assistant_rel_data = {'start_node': assistant_node, 'end_node': document_node}
            assistant_rel = create_assistant_relationship(assistant_rel_data)

            entry = ConversationEntry(
                conversation_nodes=conversation_nodes,
                document_nodes=[document_node],
                message_nodes=message_nodes,
                assistant_nodes=assistant_nodes,
                conversation_relationships=conversation_rels,
                message_relationships=message_rels,
                assistant_relationships=[assistant_rel]
            )

            conversation_entries.append(entry)

        return GraphResponse(conversation_entries=conversation_entries)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def create_document_node(data: dict) -> DocumentNode:
    required_fields = ["community", "contextCount", "embedding", "fastRP_similarity", "index", "pageRank", "text",
                       "url"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        raise ValueError(f"Missing fields: {missing_fields}")

    return DocumentNode(
        community=data['community'],
        contextCount=data['contextCount'],
        embedding=data['embedding'],
        fastRP_similarity=data['fastRP_similarity'],
        index=data['index'],
        pageRank=data['pageRank'],
        text=data['text'],
        url=data['url']
    )


def create_message_node(data: dict) -> MessageNode:
    required_fields = ["content", "embedding", "id", "postTime", "role"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        raise ValueError(f"Missing fields: {missing_fields}")

    return MessageNode(
        content=data['content'],
        embedding=data['embedding'],
        id=data['id'],
        postTime=data['postTime'].to_native(),
        role=data['role']
    )


def create_message_relationship(data: dict) -> MessageRelationship:
    required_fields = ["start_node", "end_node"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        raise ValueError(f"Missing fields: {missing_fields}")

    return MessageRelationship(
        start_node=create_message_node(data['start_node']),
        end_node=create_assistant_node(data['end_node'])
    )


def create_assistant_node(data: dict) -> AssistantNode:
    required_fields = ['content', 'fastRP_similarity', 'id', 'numDocs', 'postTime', 'rating', 'responseCommunity',
                       'role', 'similarityPR','vectorIndexSearch']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        raise ValueError(f"Missing fields: {missing_fields}")

    return AssistantNode(
        content=data['content'],
        fastRP_similarity=data['fastRP_similarity'],
        id=data['id'],
        numDocs=data['numDocs'],
        postTime=data['postTime'].to_native(),
        rating=data['rating'],
        responseCommunity=data['responseCommunity'],
        role=data['role'],
        similarityPR=data['similarityPR'],
        vectorIndexSearch=data['vectorIndexSearch']
    )


def create_conversation_node(data: dict) -> ConversationNode:
    required_fields = ["BadMessagesCount", "GoodMessagesCount", "conversation_length", "id", "llm"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        raise ValueError(f"Missing fields: {missing_fields}")

    return ConversationNode(
        BadMessagesCount=data['BadMessagesCount'],
        GoodMessagesCount=data['GoodMessagesCount'],
        conversation_length=data['conversation_length'],
        id=data['id'],
        llm=data['llm'],
        temperature=data['temperature']
    )


def create_conversation_relationship(data: dict) -> ConversationRelationship:
    required_fields = ["start_node", "end_node"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        raise ValueError(f"Missing fields: {missing_fields}")

    return ConversationRelationship(
        start_node=create_conversation_node(data['start_node']),
        end_node=create_message_node(data['end_node'])
    )


def create_assistant_relationship(data: dict) -> AssistantRelationship:
    required_fields = ["start_node", "end_node"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        raise ValueError(f"Missing fields: {missing_fields}")

    return AssistantRelationship(
        start_node=create_assistant_node(data['start_node']),
        end_node=create_document_node(data['end_node'])
    )
