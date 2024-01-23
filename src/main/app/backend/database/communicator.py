import os
import time
from typing import List, Optional

import uuid

from graphdatascience import GraphDataScience

from langchain.chat_models import ChatVertexAI, AzureChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts.prompt import PromptTemplate
import openai
import pandas as pd

from database import drivers
from tools.secret_manager import SecretManager


PUBLIC = 'false'

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

        self.driver = drivers.init_driver(uri=self.sm.access_secret_version("neo4j_dev_uri"), 
                                          username=self.sm.access_secret_version("neo4j_username"), 
                                          password=self.sm.access_secret_version("neo4j_dev_password"))
        self.database_name = self.sm.access_secret_version("neo4j_database")
        self.project = os.getenv('GCP_PROJECT_ID')
        self.region = self.sm.access_secret_version('gcp_region')

# class GraphWriter(Communicator):

#     def __init__(self) -> None:
#         super().__init__()
    
#     def log_new_conversation(self, llm, user_input):
#         """
#         This method creates a new conversation node and logs the 
#         initial user message in the neo4j database.
#         Appropriate relationships are created.
#         """

#         log_timer_start = time.perf_counter()

#         print('logging new conversation...')
#         messId = 'user-'+str(uuid.uuid4())
#         convId = 'conv-'+str(uuid.uuid4())

#         print('convId: ', convId)

#         def log(tx):
#             tx.run("""
#             create (c:Conversation)-[:FIRST]->(m:Message)
#             set c.id = $convId, c.llm = $llm,
#                 c.temperature = $temperature,
#                 c.public = toBoolean($public),
#                 m.id = $messId, m.content = $content,
#                 m.role = $role, m.postTime = datetime(),
#                 m.embedding = $embedding,
#                 m.public = toBoolean($public)
            
#             with c
#             merge (s:Session {id: $sessionId})
#             on create set s.createTime = datetime()
#             merge (s)-[:HAS_CONVERSATION]->(c)
#                       """, convId=convId, llm=llm, messId=messId, 
#                            temperature=st.session_state['temperature'],
#                            content=user_input, role='user', sessionId=st.session_state['session_id'], 
#                            embedding=st.session_state['recent_question_embedding'],
#                            public=PUBLIC)
        
#         # update the latest message in the log chain
#         st.session_state['latest_message_id'] = messId

#         try:
#             with self.driver.session(database=self.database_name) as session:
#                 session.execute_write(log)
            
#         except ConstraintError as err:
#             print(err)

#             session.close() 

#         print('conversation init & user log time: '+str(round(time.perf_counter()-log_timer_start, 4))+" seconds.")

#     def log_user(self, user_input):
#         """
#         This method logs a new user message to the neo4j database and 
#         creates appropriate relationships.
#         """

#         log_timer_start = time.perf_counter()
#         print('logging user message...')
#         prevMessId = st.session_state['latest_message_id']
#         messId = 'user-'+str(uuid.uuid4())

#         def log(tx):
#             tx.run("""
#             match (pm:Message {id: $prevMessId})
#             merge (m:Message {id: $messId})
#             set m.content = $content,
#                 m.role = $role, m.postTime = datetime(),
#                 m.embedding = $embedding, m.public = toBoolean($public)
                   
#             merge (pm)-[:NEXT]->(m)
#                       """, prevMessId=prevMessId, messId=messId, content=user_input, role='user',
#                            embedding=st.session_state['recent_question_embedding'], public=PUBLIC)
        
#         # update the latest message in the log chain
#         st.session_state['latest_message_id'] = messId

#         try:
#             with self.driver.session(database=self.database_name) as session:
#                 session.execute_write(log)
            
#         except ConstraintError as err:
#             print(err) 

#         print('user log time: '+str(round(time.perf_counter()-log_timer_start, 4))+" seconds.")

#     def log_assistant(self, assistant_output, context_indices):
#         """
#         This method logs a new assistant message to the neo4j database and 
#         creates appropriate relationships.
#         """

#         log_timer_start = time.perf_counter()

#         print('logging llm message...')
#         prevMessId = st.session_state['latest_message_id']
#         messId = 'llm-'+str(uuid.uuid4())

#         mem = st.session_state['llm_memory'].moving_summary_buffer

#         def log(tx):
#             tx.run("""
#             match (pm:Message {id: $prevMessId})
#             merge (m:Message {id: $messId})
#             set m.content = $content,
#                 m.role = $role, m.postTime = datetime(),
#                 m.numDocs = $numDocs,
#                 m.vectorIndexSearch = true,
#                 m.prompt = $prompt,
#                 m.public = toBoolean($public),
#                 m.resultingSummary = $resultingSummary
                   
#             merge (pm)-[:NEXT]->(m)

#             with m
#             unwind $contextIndices as contextIdx
#             match (d:Document)
#             where d.index = contextIdx

#             with m, d
#             merge (m)-[:HAS_CONTEXT]->(d)
#                     """, prevMessId=str(prevMessId), messId=str(messId), content=str(assistant_output), 
#                     role='assistant', contextIndices=context_indices, 
#                     numDocs=st.session_state['num_documents_for_context'], 
#                     prompt=st.session_state['general_prompt'],
#                     resultingSummary=mem,
#                     public=PUBLIC)
            
#         # update the latest message in the log chain
#         st.session_state['latest_message_id'] = messId
#         st.session_state['latest_llm_message_id'] = messId

#         try:
#             with self.driver.session(database=self.database_name) as session:
#                 session.execute_write(log)
            
#         except ConstraintError as err:
#             print(err) 

#         print('assistant log time: '+str(round(time.perf_counter()-log_timer_start, 4))+" seconds.")

#     def rate_message(self, rating_dict):
#         """
#             This message rates an LLM message given a rating and uploads
#             the rating to the database.
#         """

#         print('rating llm message...')
#         if 'latest_llm_message_id' in st.session_state:
#             rate_timer_start = time.perf_counter()

  
#             print('updating id: ', st.session_state['latest_llm_message_id'])
            
#             # parse rating info
#             message = rating_dict['text']
#             rating = 'Good' if rating_dict['score'] == '👍' else 'Bad'

#             def rate(tx):
#                 tx.run("""
#                 match (m:Message {id: $messId})
    
#                 set m.rating = $rating,
#                     m.ratingMessage = $message
#                         """, rating=rating, message=message, messId=st.session_state['latest_llm_message_id'])
                    
#             try:
#                 with self.driver.session(database=self.database_name) as session:
#                     session.execute_write(rate)
                
#             except ConstraintError as err:
#                 print(err) 

#             print('assistant rate time: '+str(round(time.perf_counter()-rate_timer_start, 4))+" seconds.")

class GraphReader(Communicator):

    def __init__(self) -> None:
        super().__init__()
        
    def retrieve_context_documents(self, question_embedding: List[float], number_of_context_documents: int = 10) -> pd.DataFrame:
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

            return tx.run(  """
                            CALL db.index.vector.queryNodes('document-embeddings', toInteger($k), $questionEmbedding)
                            YIELD node AS vDocs, score
                            return vDocs.url as url, vDocs.text as text, vDocs.index as index
                            """, questionEmbedding=question_embedding, k=number_of_context_documents
                        )
        

        # get documents from Neo4j database
        neo4j_timer_start = time.perf_counter()
        try:
            with self.driver.session(database=self.database_name) as session:
                docs = session.execute_read(neo4j_vector_index_search)
            
        except Exception as err:
            print(err) 

                
        print("Neo4j retrieval time: "+str(round(time.perf_counter()-neo4j_timer_start, 4))+" seconds.")


        return docs
    
