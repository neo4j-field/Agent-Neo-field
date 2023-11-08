import unittest
from analysis.chunk_analysis import ChunkAnalysis
from typing import List

# run from analytics $ python -m unittest tests.test_chunk_analysis
# tests only this file

class TestChunkAnalysis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        chunks = {
            "a": ["I work at Neo4j.", "I live in the United States."],
            "b": ["This is an example", "sentence."],
            "c": ["A single chunk..."]
        }
        cls.analysis = ChunkAnalysis(chunks)


    def test_character_counts(self):

        self.assertEquals(self.analysis.character_counts, [16, 28, 18, 9, 17])

    def test_word_counts(self):

        self.assertEquals(self.analysis.word_counts, [4, 6, 4, 1, 3])

    def test_average_word_lengths(self):
    
        for entry in zip(self.analysis.average_word_lengths, [3.25, 3.83, 3.75, 9, 5]):

            self.assertAlmostEquals(entry[0], entry[1], 2)

    def test_chunk_counts(self):

        self.assertEquals(self.analysis.chunk_counts, 5)


if __name__ == '__main__':
    unittest.main()