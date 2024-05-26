from neo4j import GraphDatabase
from neo4j import Driver
from typing import Any


def init_driver(uri: str, username: str, password: str) -> Driver:
    if not uri:
        raise ValueError("The URI for Neo4j is not set. Please check your configuration.")
    if not username:
        raise ValueError("The username for Neo4j is not set. Please check your configuration.")
    if not password:
        raise ValueError("The password for Neo4j is not set. Please check your configuration.")

    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        print('Driver created and connectivity verified.')
        return driver
    except Exception as e:
        print(f"Failed to create Neo4j driver due to: {str(e)}")
        raise
