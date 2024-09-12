from typing import List, Optional, Tuple, Type

import neo4j
import openai
import pandas as pd
from neo4j.exceptions import ConstraintError
from objects import AssistantMessage, Rating, UserMessage
from tools import SecretManager, timeit

from .drivers import init_driver


class Communicator:
    """
    Base class for graph reader and writer.
    """

    def __init__(self, secret_manager: SecretManager) -> None:
        self.sm = secret_manager

        openai.api_key = self.sm.access_secret_version("OPENAI_API_KEY")

        self.driver = init_driver(
            uri=self.sm.access_secret_version("NEO4J_URI"),
            username=self.sm.access_secret_version("NEO4J_USERNAME"),
            password=self.sm.access_secret_version("NEO4J_PASSWORD"),
        )

        self.database_name = self.sm.access_secret_version("NEO4J_DATABASE")
        self.project = self.sm.access_secret_version("GCP_PROJECT_ID")
        self.region = self.sm.access_secret_version("GCP_REGION")

    def close_driver(self) -> None:
        """
        Close the driver.
        """

        self.driver.close()

    def __enter__(self) -> "Communicator":
        """
        Enter the runtime context related to this object.
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[Type[BaseException]],
    ) -> bool:
        """
        Exit the runtime context and close the driver.
        :param exc_type: Exception type
        :param exc_value: Exception value
        :param traceback: Traceback object
        :return: True if no exception occurred, False otherwise
        """
        self.close_driver()
        if exc_type is not None:
            print(f"Exception occurred: {exc_type}, {exc_value}")
            return False
        return True


class GraphWriter(Communicator):
    def __init__(self, secret_manager: SecretManager) -> None:
        super().__init__(secret_manager)

    def log_new_conversation(
        self, message: UserMessage, llm_type: str, temperature: float
    ) -> None:
        """
        This method creates a new conversation node and logs the
        initial user message in the neo4j database.
        Appropriate relationships are created.
        """

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
            merge (s)-[:HAS_CONVERSATION]->(c)""",
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
        :param message:
        :param previous_message_id:
        :return:
        """

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

            merge (pm)-[:NEXT]->(m)""",
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
    ) -> None:
        """
        This method logs a new assistant message to the neo4j database and
        creates appropriate relationships.
        """

        mem = "None"

        def log(tx):
            tx.run(
                """
            MATCH (pm:Message {id: $prevMessId})

            MERGE (m:Assistant {id: $messId})
            SET m.content = $content,
                m.role = $role,
                m.postTime = datetime(),
                m.numDocs = $numDocs,
                m.vectorIndexSearch = true,
                m.prompt = $prompt,
                m.public = toBoolean($public),
                m.resultingSummary = $resultingSummary

            MERGE (pm)-[:NEXT]->(m)

            WITH m
            UNWIND $contextIndices as contextIdx
            MATCH (d:Document)
            WHERE d.index = contextIdx

            WITH m, d
            MERGE (m)-[:HAS_CONTEXT]->(d)""",
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

    def rate_message(self, rating: Rating) -> None:
        """
        Rate an LLM message given a rating and uploads
        the rating to the database.
        :param rating:
        :return:
        """

        def rate(tx):
            tx.run(
                """
            MATCH (m:Message {id: $messId})

            SET m.rating = $rating,
                m.ratingMessage = $message""",
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
        :param ids:
        :return:
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
        :param id:
        :param label:
        :return:
        """

        def write_node(tx) -> None:
            prompt = (
                "merge (n:" + label + "{id: $id})"
                if not label == "Document"
                else "merge (n:" + label + "{index: $id})"
            )
            tx.run(prompt, id=id)

        try:
            with self.driver.session(database=self.database_name) as session:
                session.execute_write(write_node)

        except ConstraintError as err:
            print(err)
            session.close()


class GraphReader(Communicator):
    def __init__(self, secret_manager: SecretManager) -> None:
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

        :param question_embedding:
        :param number_of_context_documents:
        :return:
        """

        @timeit
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

        try:
            with self.driver.session(database=self.database_name) as session:
                docs = session.execute_read(neo4j_vector_index_search)

        except Exception as err:
            print(err)

        return pd.DataFrame(docs, columns=["url", "text", "index"])

    def retrieve_context_documents_by_topic(
        self,
        question_embedding: List[float],
        number_of_topics: int = 3,
        documents_per_topic: int = 4,
    ):
        """
        This function takes the user question and creates an embedding of it
        using a vertexai model.
        Cosine similarity is run on the embedding against the embeddings in the
        Neo4j database to topic summaries most similar to the question.
        The most relevant documents for each topic are retrieved.
        The top n documents with their URLs are returned as context.

        :param question_embedding:
        :param number_of_topics:
        :param documents_per_topic:
        :return:
        """

        @timeit
        def topical_neo4j_vector_index_search(tx):
            """
            This method runs vector similarity search on the document embeddings against the question embedding.
            """

            return tx.run(
                """
                            CALL db.index.vector.queryNodes('topic_group_summary_embeddings', toInteger($k),
                            $questionEmbedding)
                            YIELD node AS g, score
                            MATCH (g)<-[:IN_GROUP]-()<-[h:HAS_TOPIC]-(vDocs)
                            WHERE h.rankAlpha50 <= toInteger($documents_per_topic)
                            return vDocs.url as url, vDocs.text as text, vDocs.index as index
                            """,
                questionEmbedding=question_embedding,
                k=number_of_topics,
                documents_per_topic=documents_per_topic,
            ).values()

        try:
            with self.driver.session(database=self.database_name) as session:
                docs = session.execute_read(topical_neo4j_vector_index_search)

        except Exception as err:
            print(err)
            session.close()
        return pd.DataFrame(docs, columns=["url", "text", "index"])

    def retrieve_conversation_history(self, conversation_id: str) -> List[Tuple]:
        """
        This function grabs the entire conversation history and the referenced document chunks.
        :param conversation_id:
        :return: a list of tuples.
        tuple[0] is the neo4j message path
        tuple[1] is the neo4j document path

        these are returned by the inline cypher query
        """

        @timeit
        def retrieve_conversation(tx) -> neo4j.EagerResult:
            return tx.run(
                """
                MATCH (c:Conversation {id: $conversation_id})
                WITH c
                MATCH (c) - [:FIRST] -> (startMessage:Message)
                WITH c, startMessage
                MATCH messagePath = (c)-[:FIRST]-(startMessage)
                ((question:Message)-[:NEXT]->(response)){1,25}
                WITH messagePath, startMessage, response
                UNWIND response as resp
                MATCH documentPaths = (resp)-[:HAS_CONTEXT]->(:Document)
                WITH messagePath, documentPaths
                RETURN documentPaths, messagePath as messagePaths
                LIMIT 50""",
                conversation_id=conversation_id,
            ).to_eager_result()

        try:
            with self.driver.session(database=self.database_name) as session:
                conversation_result: neo4j.EagerResult = session.execute_read(
                    retrieve_conversation
                )
                conversation_paths: List[Tuple] = [
                    tuple(record) for record in conversation_result.records
                ]

        except Exception as err:
            print(f"Error retrieving conversation records: {err}")
            session.close()
            raise

        return conversation_paths

    def match_by_id(self, ids: List[str]) -> int:
        """
        Match nodes based on provided ids and return count.

        :param ids:
        :return:
        """

        @timeit
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

        @timeit
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
        rate messages
        :param assistant_message_id:
        :return:
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
