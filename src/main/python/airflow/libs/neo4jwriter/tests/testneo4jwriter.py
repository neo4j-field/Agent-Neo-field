import unittest
import pandas as pd
import numpy as np
import random
import string
from ..neo4jwriter import Neo4jWriter

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def generate_random_url():
    return f"https://{generate_random_string()}.com"

def generate_random_embedding(dimensions=50):
    return np.random.rand(dimensions).tolist()

class TestNeo4jWriter(unittest.TestCase):

    def test_neo4j_writer(self):
        # Number of rows in the DataFrame
        num_rows = 100000

        # Creating the DataFrame
        params = pd.DataFrame({
            'index': range(num_rows),
            'chunk_text': [generate_random_string(random.randint(5, 15)) for _ in range(num_rows)],
            'chunk_len': [random.randint(1, 500) for _ in range(num_rows)],
            'chunk_url': [generate_random_url() for _ in range(num_rows)],
            'source_type': [random.choice(['Web', 'Book', 'Journal', 'Article']) for _ in range(num_rows)],
            'topic': [generate_random_string(random.randint(3, 8)) for _ in range(num_rows)],
            'embedding': [generate_random_embedding() for _ in range(num_rows)]
        }).to_dict("records")


        cypher_file = '/src/main/python/resources/cypher/documents.cypher'



        with open(cypher_file, 'r') as file:
            cypher = file.read()


        writer = Neo4jWriter()

        writer.batch_write(cypher_query=cypher,params=params)







