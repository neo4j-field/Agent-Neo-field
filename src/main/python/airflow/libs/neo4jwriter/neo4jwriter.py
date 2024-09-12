from typing import Any, Dict, Iterator, List, Optional

from neo4j import GraphDatabase, Transaction


class Neo4jWriter:
    def __init__(
        self,
        neo4j_url: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
        database: Optional[str] = None,
    ):
        self.driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_password))
        self.database = database

    def batch_write(self, cypher_query: str, params: List[Dict[str, Any]], batch_size: int = 10000):
        with self.driver.session(database=self.database) as session:
            for batch in Neo4jWriter._batch_parameters(params, batch_size):
                packaged_params = {"params": batch}

                def tx_function(tx):
                    return self.neo4j_tx_function(
                        tx=tx,
                        params=packaged_params,
                        cypher_query=cypher_query,
                    )

                session.execute_write(tx_function)

    def neo4j_tx_function(self, tx: Transaction, params: List[Dict[str, Any]], cypher_query: str) -> None:
        tx.run(cypher_query, parameters=params)

    def build_indexes(self, index_list=List[str]):
        for index in index_list:

            def tx_function(tx):
                return self.neo4j_tx_function(tx=tx, params=[])

            self.session.execute_write(tx_function)

    @staticmethod
    def _batch_parameters(lst: List[Any], batch_size: int) -> Iterator[List[Any]]:
        for i in range(0, len(lst), batch_size):
            yield lst[i: i + batch_size]
