import os
import unittest
from google.cloud import storage
from ..scraper.scrape import WebContentChunker
from langchain.schema.document import Document
from typing import List

# run from python/scrape $ python -m unittest discover -t .. -p "test_web*.py" 
# tests only this file

class TestWebContentChunker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.chunker = WebContentChunker()
        cls.chunker._chunked_documents = [
            Document(page_content="abc", metadata={"source": "site_1"}),
            Document(page_content="def", metadata={"source": "site_1"}),
            Document(page_content="123", metadata={"source": "site_2"}),
            Document(page_content="456", metadata={"source": "site_3"})
        ]

    def test_chunk_texts(self):
        
        result = self.chunker.chunk_texts

        self.assertIsInstance(result[0], str)
        self.assertEquals(len(result), 4)


    def test_chunk_urls(self):

        result = self.chunker.chunk_urls

        self.assertEquals(len(result), 3)

    def test_chunks_as_dict(self):

        result = self.chunker.chunks_as_dict
        self.assertEquals(len(result['site_1']), 2)
        self.assertEquals(len(result['site_2']), 1)
        


if __name__ == '__main__':
    unittest.main()