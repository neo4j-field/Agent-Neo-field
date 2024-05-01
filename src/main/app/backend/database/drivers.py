from neo4j import GraphDatabase, Driver


def init_driver(uri, username, password) -> Driver:
    """
    Initiate the Neo4j Driver.
    """
    d = GraphDatabase.driver(uri, auth=(username, password))
    d.verify_connectivity()
    d.verify_authentication()
    print("driver created. connection verified. auth verified.")
    return d
