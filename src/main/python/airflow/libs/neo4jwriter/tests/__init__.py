import os
from typing import List, Any, Dict, Iterator, Callable
from neo4j import GraphDatabase, Transaction


class Neo4jWriter:
    def __init__(self, neo4j_url: str = 'neo4j://54.68.133.241:7687',
                 neo4j_user: str = 'neo4j',
                 neo4j_password: str = 'centraldev1100',
                 database: str = 'cumminssoftwarebom'):
        self.driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_password))
        self.session = self.driver.session(database=database)

    def batch_write(self, func: Callable[[Transaction, List[Dict[str, Any]]], None],
                    params: List[Dict[str, Any]], batch_size: int = 10000):
        with self.driver.session(database=self.database) as session:
            for batch in Neo4jWriter.batch_parameters(params, batch_size):
                session.execute_write(func, {'params': batch})

    @staticmethod
    def neo4j_callable(cypher_query: str, tx: Transaction, params: List[Dict[str, Any]]) -> None:
        tx.run(cypher_query, parameters=params)

    @staticmethod
    def batch_parameters(lst: List[Any], batch_size: int) -> Iterator[List[Any]]:
        for i in range(0, len(lst), batch_size):
            yield lst[i:i + batch_size]
