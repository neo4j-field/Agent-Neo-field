from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, validator

# todo
'''
The Database schema needs to be normalized. 

There are a bunch of different permutations of properties on nodes with the same label set.

There are also different permutations of property types attached to them,
one property on one node might be a datetime where the same property on another node is a string.
'''


class AssistantNode(BaseModel):
    content: str = Field(description="Content of the assistant's response")
    fastRP_similarity: List[float] = Field(description="FastRP similarity scores")
    id: str = Field(description="ID of the node")
    numDocs: int = Field(description="Number of documents associated")
    postTime: datetime = Field(description="Post time of the response")
    rating: str = Field(description="Rating of the response")
    responseCommunity: int = Field(description="Response community ID")
    role: str = Field(description="Role of the node")
    similarityPR: float = Field(description="Similarity PageRank score")
    vectorIndexSearch: bool = Field(description="vector index")


class ConversationNode(BaseModel):
    BadMessagesCount: int = Field(description="Count of bad messages in the conversation")
    GoodMessagesCount: int = Field(description="Count of good messages in the conversation")
    conversation_length: int = Field(description="Length of the conversation")
    id: str = Field(description="Conversation ID")
    llm: str = Field(description="The LLM used for the conversation")
    temperature: float = Field(description="llm temperature")


class DocumentNode(BaseModel):
    """
    Contains document (node) information.
    """
    community: int = Field(description="community the node belongs too")
    contextCount: int = Field("context count")
    embedding: list[float] = Field(description="text embedding")
    fastRP_similarity: list[float] = Field(description="fast-rp similarity")
    index: int = Field(description="index")
    pageRank: float = Field(description="page rank score")
    text: str = Field(description="text chunk")
    url: str = Field(description="url")


class SessionNode(BaseModel):
    conversation_count: int = Field(description="Count of conversations in the session")
    createTime: datetime = Field(description="Creation time of the session")
    session_id: str = Field(description="Session ID")


class MessageNode(BaseModel):
    content: str = Field(description="Content of the message")
    embedding: List[float] = Field(description="Embedding vector of the message")
    id: str = Field(description="ID of the message node")
    postTime: datetime = Field(description="Post time of the message")
    role: str = Field(description="Role of the sender (user/assistant)")


class ConversationRelationship(BaseModel):
    start_node: ConversationNode = Field(description="start node of the conversation")
    end_node: MessageNode = Field(description="first message in the conversation")


class MessageRelationship(BaseModel):
    start_node: MessageNode = Field(description="start message node in relationship")
    end_node: AssistantNode = Field(description="end message node in relationship")


class AssistantRelationship(BaseModel):
    start_node: AssistantNode = Field(description="start")
    end_node: DocumentNode = Field(description="end")


class ConversationEntry(BaseModel):
    """
    Contains the conversation entry information. a conversation entry is both the question/response sequence and the referenced RAG documents.
    """
    conversation_nodes: List[ConversationNode]
    document_nodes: List[DocumentNode]
    message_nodes: List[MessageNode]
    assistant_nodes: List[AssistantNode]
    conversation_relationships: List[ConversationRelationship]
    message_relationships: List[MessageRelationship]
    assistant_relationships: List[AssistantRelationship]
