import os
import time
from typing import List, Optional, Union

from neo4j.exceptions import ConstraintError
import openai
import pandas as pd

from database import drivers
from tools.secret_manager import SecretManager
from objects.nodes import UserMessage, AssistantMessage
from objects.rating import Rating


class Communicator:
    """
    Base class for graph reader and writer.
    """

    def __init__(self, secret_manager: Optional[SecretManager] = None) -> None:
        
        if secret_manager is not None:
            print("Grabbing secrets from GCP.")
            # AUTHENTICATE OPENAI
            openai.api_key = secret_manager.access_secret_version("openai_key")
            openai.api_version = secret_manager.access_secret_version("openai_version")
            self.driver = drivers.init_driver(
                uri=secret_manager.access_secret_version(f"neo4j_{os.environ.get('DATABASE_TYPE')}_uri"),
                username=secret_manager.access_secret_version("neo4j_username"),
                password=secret_manager.access_secret_version(f"neo4j_{os.environ.get('DATABASE_TYPE')}_password")
                    )
            self.database_name = secret_manager.access_secret_version("neo4j_database")
            self.project = os.getenv("GCP_PROJECT_ID")
            self.region = secret_manager.access_secret_version("gcp_region")
        else:
            print("Grabbing secrets from environment variables.")
            openai.api_key = os.environ.get("OPENAI_API_KEY")
            openai.api_version = os.environ.get("OPENAI_VERSION")
            self.driver = drivers.init_driver(
                uri=os.environ.get("NEO4J_URI"),
                username=os.environ.get("NEO4J_USERNAME"),
                password=os.environ.get('NEO4J_PASSWORD')
            )
            self.database_name = os.environ.get("NEO4J_DATABASE")
            self.project = os.environ.get("GCP_PROJECT_ID")
            self.region = os.environ.get("GCP_REGION")



    def close_driver(self) -> None:
        """
        Close the driver.
        """

        self.driver.close()


class GraphWriter(Communicator):

    def __init__(self, secret_manager: Optional[SecretManager] = None) -> None:
        super().__init__(secret_manager)

    def log_new_conversation(
        self, message: UserMessage, llm_type: str, temperature: float
    ) -> None:
        """
        This method creates a new conversation node and logs the
        initial user message in the neo4j database.
        Appropriate relationships are created.
        """

        print("logging new conversation...")

        print("convId: ", message.conversation_id)

        def log(tx):
            tx.run(
                """
            create (c:Conversation)-[:FIRST]->(m:Message)
            set c.id = $convId, 
                c.llm = $llm,
                c.temperature = $temperature,
                c.public = toBoolean($public),
                m.id = $messId, 
                m.content = $content,
                m.role = $role, 
                m.postTime = datetime(),
                m.public = toBoolean($public)

            with c, m
            call db.create.setNodeVectorProperty(m, 'embedding', $embedding)
            
            merge (s:Session {id: $sessionId})
            on create set s.createTime = datetime()
            merge (s)-[:HAS_CONVERSATION]->(c)
                      """,
                sessionId=message.session_id,
                convId=message.conversation_id,
                messId=message.message_id,
                llm=llm_type,
                temperature=temperature,
                content=message.content,
                embedding=message.embedding,
                role="user",
                public=message.public,
            )

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

        print("logging user message...")

        def log(tx):
            tx.run(
                """
            match (pm:Message {id: $prevMessId})
            merge (m:Message {id: $messId})
            set m.content = $content,
                m.role = $role, 
                m.postTime = datetime(),
                m.public = toBoolean($public)
            
            with m, pm
            call db.create.setNodeVectorProperty(m, 'embedding', $embedding)

            merge (pm)-[:NEXT]->(m)
                      """,
                prevMessId=previous_message_id,
                messId=message.message_id,
                content=message.content,
                embedding=message.embedding,
                role="user",
                public=message.public,
            )

        try:
            with self.driver.session(database=self.database_name) as session:
                session.execute_write(log)

        except ConstraintError as err:
            print(err)
            session.close()

    def log_assistant(
        self,
        message: AssistantMessage,
        previous_message_id: str,
        context_ids: List[str],
    ):
        """
        This method logs a new assistant message to the neo4j database and
        creates appropriate relationships.
        """

        print("logging llm message...")

        mem = "None"

        def log(tx):
            tx.run(
                """
            match (pm:Message {id: $prevMessId})
            merge (m:Message {id: $messId})
            set m.content = $content,
                m.role = $role, 
                m.postTime = datetime(),
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
                    """,
                prevMessId=previous_message_id,
                messId=message.message_id,
                content=message.content,
                role="assistant",
                contextIndices=context_ids,
                numDocs=message.number_of_documents,
                prompt=message.prompt,
                resultingSummary=mem,
                public=message.public,
            )

        try:
            with self.driver.session(database=self.database_name) as session:
                session.execute_write(log)

        except ConstraintError as err:
            print(err)
            session.close()

    def rate_message(self, rating: Rating):
        """
        Rate an LLM message given a rating and uploads
        the rating to the database.
        """

        print("rating llm message...")

        def rate(tx):
            tx.run(
                """
            match (m:Message {id: $messId})

            set m.rating = $rating,
                m.ratingMessage = $message
                    """,
                rating=rating.value,
                message=rating.message,
                messId=rating.message_id,
            )

        try:
            with self.driver.session(database=self.database_name) as session:
                session.execute_write(rate)

        except ConstraintError as err:
            print(err)
            session.close()

    def delete_by_id(self, ids: List[str]) -> None:
        """
        Delete nodes and relationships based on provided ids.
        """

        def delete_nodes_and_rels(tx):
            tx.run(
                """
                unwind $ids as id
                match (n {id: id})-[r]-()
                detach delete n, r
                """,
                ids=ids,
            )

        def delete_nodes(tx):
            tx.run(
                """
                unwind $ids as id
                match (n {id: id})
                delete n
                """,
                ids=ids,
            )

        def delete_document_nodes(tx):
            tx.run(
                """
                unwind $ids as id
                match (n {index: id})
                delete n
                """,
                ids=ids,
            )

        try:
            with self.driver.session(database=self.database_name) as session:
                session.execute_write(delete_nodes_and_rels)
                session.execute_write(delete_nodes)
                session.execute_write(delete_document_nodes)

        except ConstraintError as err:
            print(err)
            session.close()

    def write_dummy_node(self, id: str, label: str) -> None:
        """
        Create a dummy node for testing.
        """

        def write_node(tx):
            prompt = (
                "merge (n:" + label + "{id: $id})"
                if not label == "Document"
                else "merge (n:" + label + "{index: $id})"
            )
            tx.run(prompt, id=id)
            print(prompt)

        try:
            with self.driver.session(database=self.database_name) as session:
                session.execute_write(write_node)

        except ConstraintError as err:
            print(err)
            session.close()


class GraphReader(Communicator):

    def __init__(self, secret_manager: Optional[SecretManager] = None) -> None:
        super().__init__(secret_manager)

    def retrieve_context_documents(
        self, question_embedding: List[float], number_of_context_documents: int = 10
    ) -> pd.DataFrame:
        """
        This function takes the user question and creates an embedding of it
        using a vertexai model.
        Cosine similarity is ran on the embedding against the embeddings in the
        Neo4j database to find documents that will be used to construct
        the context.
        The top n documents with their URLs are returned as context.
        """

        def neo4j_vector_index_search(tx):
            """
            This method runs vector similarity search on the document embeddings against the question embedding.
            """

            return tx.run(
                """
                            CALL db.index.vector.queryNodes('document-embeddings', toInteger($k), $questionEmbedding)
                            YIELD node AS vDocs, score
                            return vDocs.url as url, vDocs.text as text, vDocs.index as index
                            """,
                questionEmbedding=question_embedding,
                k=number_of_context_documents,
            ).values()

        # get documents from Neo4j database
        neo4j_timer_start = time.perf_counter()
        try:
            with self.driver.session(database=self.database_name) as session:
                docs = session.execute_read(neo4j_vector_index_search)

        except Exception as err:
            print(err)
            session.close()

        print(
            "Neo4j retrieval time: "
            + str(round(time.perf_counter() - neo4j_timer_start, 4))
            + " seconds."
        )

        return pd.DataFrame(docs, columns=["url", "text", "index"])

    def retrieve_context_documents_by_topic(
        self,
        question_embedding: List[float],
        number_of_topics: int = 3,
        documents_per_topic: int = 4,
    ) -> pd.DataFrame:
        """
        This function takes the user question and creates an embedding of it
        using a vertexai model.
        Cosine similarity is run on the embedding against the embeddings in the
        Neo4j database to topic summaries most similar to the question.
        The most relevant documents for each topic are retrieved.
        The top n documents with their URLs are returned as context.
        """

        def topical_neo4j_vector_index_search(tx):
            """
            This method runs vector similarity search on the document embeddings against the question embedding.
            """

            return tx.run(
                """
                            CALL db.index.vector.queryNodes('topic_group_summary_embeddings', toInteger($k), $questionEmbedding)
                            YIELD node AS g, score
                            MATCH (g)<-[:IN_GROUP]-()<-[h:HAS_TOPIC]-(vDocs)
                            WHERE h.rankAlpha50 <= toInteger($documents_per_topic)
                            return vDocs.url as url, vDocs.text as text, vDocs.index as index
                            """,
                questionEmbedding=question_embedding,
                k=number_of_topics,
                documents_per_topic=documents_per_topic,
            ).values()

        # get documents from Neo4j database
        neo4j_timer_start = time.perf_counter()
        try:
            with self.driver.session(database=self.database_name) as session:
                docs = session.execute_read(topical_neo4j_vector_index_search)

        except Exception as err:
            print(err)
            session.close()

        print(
            "Neo4j retrieval time: "
            + str(round(time.perf_counter() - neo4j_timer_start, 4))
            + " seconds."
        )

        return pd.DataFrame(docs, columns=["url", "text", "index"])

    def match_by_id(self, ids: List[str]) -> int:
        """
        Match nodes based on provided ids and return count.
        """

        def match_nodes(tx):
            return (
                tx.run(
                    """
                unwind $ids as id
                match (n {id: id})
                return count(distinct n)
                """,
                    ids=ids,
                )
                .single()
                .value()
            )

        def match_document_nodes(tx):
            return (
                tx.run(
                    """
                unwind $ids as id
                match (n {index: id})
                return count(distinct n)
                """,
                    ids=ids,
                )
                .single()
                .value()
            )

        try:
            with self.driver.session(database=self.database_name) as session:
                num_messages = session.execute_read(match_nodes)
                print(f"messages {num_messages}")
                num_documents = session.execute_read(match_document_nodes)
                print(f"docs {num_documents}")

        except ConstraintError as err:
            print(err)
            session.close()

        return num_documents + num_messages

    def get_message_rating(self, assistant_message_id: str) -> str:
        """
        Retrieve a message rating.
        """

        def get(tx):
            return tx.run(
                """
                match (n:Message {id: $id})
                return n.id as id, n.rating as rating, n.ratingMessage as rating_message
                """,
                id=assistant_message_id,
            ).values()

        try:
            with self.driver.session(database=self.database_name) as session:
                res = session.execute_read(get)[0]

        except ConstraintError as err:
            print(err)
            session.close()

        return res
