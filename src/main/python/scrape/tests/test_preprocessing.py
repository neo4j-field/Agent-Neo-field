import os
import unittest
from google.cloud import storage
from ..scraper.preprocessing import fix_neo4j_spelling
from typing import List

# run from python/scrape $ python -m unittest discover -t .. -p "test_prepro*.py" 
# tests only this file

class TestPreprocessing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        
        pass

    def test_fix_neo4j_spelling(self):

        bad_words = ["NE forj", "Neo forj", "neoa"]

        for word in bad_words:
            self.assertEquals(fix_neo4j_spelling(word), "Neo4j")
        

if __name__ == '__main__':
    unittest.main()