import os
import time
from typing import List, Optional

import uuid
from langchain.chat_models import ChatVertexAI, AzureChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts.prompt import PromptTemplate
from neo4j.exceptions import ConstraintError
import openai
import pandas as pd

from .drivers import init_driver
from tools import SecretManager
from objects import UserMessage, AssistantMessage
from objects import Rating


# PUBLIC = 'false'

# AUTHENTICATE SERVICE ACCOUNT  
# google_credentials = service_account.Credentials.from_service_account_info(
#     sm.access_secret_version("google_service_account")
# )


class Communicator:
    """
    The constructor expects an instance of the Neo4j Driver, which will be
    used to interact with Neo4j.
    This class contains methods necessary to interact with the Neo4j database
    and manage conversations with the chosen LLM.
    """

    sm = SecretManager()

    # AUTHENTICATE OPENAI
    openai.api_key = sm.access_secret_version('openai_key')
    openai.api_version = sm.access_secret_version('openai_version')

    def __init__(self) -> None:
        self.driver = init_driver(
            uri=self.sm.access_secret_version(f"neo4j_{os.environ.get('DATABASE_TYPE')}_uri"),
            username=self.sm.access_secret_version("neo4j_username"),
            password=self.sm.access_secret_version(f"neo4j_{os.environ.get('DATABASE_TYPE')}_password"))
        self.database_name = self.sm.access_secret_version("neo4j_database")
        self.project = os.getenv('GCP_PROJECT_ID')
        self.region = self.sm.access_secret_version('gcp_region')


class GraphWriter(Communicator):

    def __init__(self) -> None:
        super().__init__()

    def log_new_conversation(self, message: UserMessage, llm_type: str, temperature: float) -> None:
        """
        This method creates a new conversation node and logs the 
        initial user message in the neo4j database.
        Appropriate relationships are created.
        """

        print('logging new conversation...')

        print('convId: ', message.conversation_id)

        def log(tx):
            tx.run("""
            create (c:Conversation)-[:FIRST]->(m:Message)
            set c.id = $convId, c.llm = $llm,
                c.temperature = $temperature,
                c.public = toBoolean($public),
                m.id = $messId, m.content = $content,
                m.role = $role, m.postTime = datetime(),
                m.embedding = $embedding,
                m.public = toBoolean($public)
            
            with c
            merge (s:Session {id: $sessionId})
            on create set s.createTime = datetime()
            merge (s)-[:HAS_CONVERSATION]->(c)
                      """, sessionId=message.session_id,
                   convId=message.conversation_id,
                   messId=message.message_id,
                   llm=llm_type,
                   temperature=temperature,
                   content=message.content,
                   embedding=message.embedding,
                   role='user',
                   public=message.public)

        try:
            with self.driver.session(database=self.database_name) as session:
                session.execute_write(log)

        except ConstraintError as err:
            print(err)

            session.close()

    def log_user(self, message: UserMessage, previous_message_id: str) -> None:
        """
        This method logs a new user message to the neo4j database and 
        creates appropriate relationships.
        """

        print('logging user message...')

        def log(tx):
            tx.run("""
            match (pm:Message {id: $prevMessId})
            merge (m:Message {id: $messId})
            set m.content = $content,
                m.role = $role, m.postTime = datetime(),
                m.embedding = $embedding, m.public = toBoolean($public)
                   
            merge (pm)-[:NEXT]->(m)
                      """, prevMessId=previous_message_id,
                   messId=message.message_id,
                   content=message.content,
                   embedding=message.content,
                   role='user',
                   public=message.public)

        try:
            with self.driver.session(database=self.database_name) as session:
                session.execute_write(log)

        except ConstraintError as err:
            print(err)

    def log_assistant(self, message: AssistantMessage, previous_message_id: str, context_ids: List[str]):
        """
        This method logs a new assistant message to the neo4j database and 
        creates appropriate relationships.
        """

        print('logging llm message...')

        mem = "None"

        def log(tx):
            tx.run("""
            match (pm:Message {id: $prevMessId})
            merge (m:Message {id: $messId})
            set m.content = $content,
                m.role = $role, m.postTime = datetime(),
                m.numDocs = $numDocs,
                m.vectorIndexSearch = true,
                m.prompt = $prompt,
                m.public = toBoolean($public),
                m.resultingSummary = $resultingSummary
                   
            merge (pm)-[:NEXT]->(m)

            with m
            unwind $contextIndices as contextIdx
            match (d:Document)
            where d.index = contextIdx

            with m, d
            merge (m)-[:HAS_CONTEXT]->(d)
                    """, prevMessId=previous_message_id,
                   messId=message.message_id,
                   content=message.content,
                   role='assistant',
                   contextIndices=context_ids,
                   numDocs=message.number_of_documents,
                   prompt=message.prompt,
                   resultingSummary=mem,
                   public=message.public)

        try:
            with self.driver.session(database=self.database_name) as session:
                session.execute_write(log)

        except ConstraintError as err:
            print(err)

    def rate_message(self, rating: Rating):
        """
            Rate an LLM message given a rating and uploads
            the rating to the database.
        """

        print('rating llm message...')

        def rate(tx):
            tx.run("""
            match (m:Message {id: $messId})

            set m.rating = $rating,
                m.ratingMessage = $message
                    """, rating=rating.value, message=rating.message, messId=rating.message_id)

        try:
            with self.driver.session(database=self.database_name) as session:
                session.execute_write(rate)

        except ConstraintError as err:
            print(err)


class GraphReader(Communicator):

    def __init__(self) -> None:
        super().__init__()

    def retrieve_context_documents(self, question_embedding: List[float],
                                   number_of_context_documents: int = 10) -> pd.DataFrame:
        '''
        This function takes the user question and creates an embedding of it
        using a vertexai model. 
        Cosine similarity is ran on the embedding against the embeddings in the 
        Neo4j database to find documents that will be used to construct
        the context. 
        The top n documents with their URLs are returned as context.
        '''

        def neo4j_vector_index_search(tx):
            """
            This method runs vector similarity search on the document embeddings against the question embedding.
            """

            return tx.run("""
                            CALL db.index.vector.queryNodes('document-embeddings', toInteger($k), $questionEmbedding)
                            YIELD node AS vDocs, score
                            return vDocs.url as url, vDocs.text as text, vDocs.index as index
                            """, questionEmbedding=question_embedding, k=number_of_context_documents
                          ).values()

        # get documents from Neo4j database
        neo4j_timer_start = time.perf_counter()
        try:
            with self.driver.session(database=self.database_name) as session:
                docs = session.execute_read(neo4j_vector_index_search)

        except Exception as err:
            print(err)

        print("Neo4j retrieval time: " + str(round(time.perf_counter() - neo4j_timer_start, 4)) + " seconds.")

        return pd.DataFrame(docs, columns=["url", "text", "index"])

    def retrieve_context_documents_by_topic(self, question_embedding: List[float],
                                            number_of_topics: int = 3,
                                            documents_per_topic: int = 4) -> pd.DataFrame:
        '''
        This function takes the user question and creates an embedding of it
        using a vertexai model.
        Cosine similarity is run on the embedding against the embeddings in the
        Neo4j database to topic summaries most similar to the question.
        The most relevant documents for each topic are retrieved.
        The top n documents with their URLs are returned as context.
        '''

        def topical_neo4j_vector_index_search(tx):
            """
            This method runs vector similarity search on the document embeddings against the question embedding.
            """

            return tx.run("""
                            CALL db.index.vector.queryNodes('topic_group_summary_embeddings', toInteger($k), questionEmbedding)
                            YIELD node AS g, score
                            MATCH (g)<-[:IN_GROUP]-()<-[h:HAS_TOPIC]-(vDocs)
                            WHERE h.rankAlpha50 <= toInteger($documents_per_topic)
                            return vDocs.url as url, vDocs.text as text, vDocs.index as index
                            """, questionEmbedding=question_embedding, k=number_of_topics,
                          docs_per_topic=documents_per_topic
                          ).values()

        # get documents from Neo4j database
        neo4j_timer_start = time.perf_counter()
        try:
            with self.driver.session(database=self.database_name) as session:
                docs = session.execute_read(topical_neo4j_vector_index_search)

        except Exception as err:
            print(err)

        print("Neo4j retrieval time: " + str(round(time.perf_counter() - neo4j_timer_start, 4)) + " seconds.")

        return pd.DataFrame(docs, columns=["url", "text", "index"])
