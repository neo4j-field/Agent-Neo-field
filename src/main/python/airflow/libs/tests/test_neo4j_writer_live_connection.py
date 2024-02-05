import unittest
from ..neo4jwriter import Neo4jWriter


class TestNeo4jWrite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        env_file_path = '/Users/alexanderfournier/Downloads/Agent-Neo-field/src/main/python/airflow/tasks/gcpfetch/env.json'

        with open(env_file_path, 'r') as f:
            config = json.load(f)

        cls.neo4j_user = config.get('NEO4J_USERNAME')
        cls.neo4j_password = config.get('NEO4J_PASSWORD')
        cls.neo4j_uri = config.get('NEO4J_URI')
        cls.neo4j_database = config.get('NEO4J_URI')

    def test_neo4j_write(self):
        neo4j_writer = Neo4jWriter(neo4j_url=self.neo4j_uri, neo4j_user=self.neo4j_user,
                                   neo4j_password=self.neo4j_password, database=self.neo4j_database)



