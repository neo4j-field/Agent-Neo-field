from typing import List, Any, Dict, Iterator, Callable, Union
from neo4j import GraphDatabase, Transaction


class Neo4jWriter:
    def __init__(self, neo4j_url: str = '',
                 neo4j_user: str = '',
                 neo4j_password: str = '',
                 database: str = ''):
        self.driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_password))
        self.database = database

    def batch_write(self, cypher_query: str, params: List[Dict[str, Any]], batch_size: int = 10000):
        with self.driver.session(database=self.database) as session:
            for batch in Neo4jWriter._batch_parameters(params, batch_size):
                packaged_params = {'params': batch}
                tx_function = lambda tx: self.neo4j_tx_function(tx=tx, cypher_query=cypher_query,params=packaged_params)
                session.execute_write(tx_function)

    def neo4j_tx_function(self, tx: Transaction, params: List[Dict[str, Any]], cypher_query: str) -> None:
        tx.run(cypher_query, parameters=params)


    def build_indexes(self,index_list = List[str]):
        for index in index_list:
            tx_function = lambda tx: self.neo4j_tx_function(tx,[],index)
            self.session.execute_write(tx_function)

    @staticmethod
    def _batch_parameters(lst: List[Any], batch_size: int) -> Iterator[List[Any]]:
        for i in range(0, len(lst), batch_size):
            yield lst[i:i + batch_size]
