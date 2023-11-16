
from typing import List, Dict
import itertools
from langchain.schema.document import Document


class ChunkAnalysis:
    """
    This class provides a framework for analyzing the chunking method used prior to uploading data into the graph.

    Input:
        Dictionary of {source: [chunk_1, chunk_2, ..., chunk_n]}
    """

    def __init__(self, chunks: Dict[str, List[str]]) -> None:

        self.chunks = chunks

    @property
    def character_counts(self) -> List[int]:
        
        return [len(chunk) for chunk in itertools.chain.from_iterable(self.chunks.values())]

    @property
    def word_counts(self) -> List[int]:

        return [len(chunk.split(" ")) for chunk in itertools.chain.from_iterable(self.chunks.values())]

    @property
    def average_word_lengths(self) -> List[float]:

        word_lists = [chunk.split(" ") for chunk in itertools.chain.from_iterable(self.chunks.values())]
        return [sum([len(word) for word in words]) / len(words) for words in word_lists]

    @property
    def chunk_count(self) -> int:

        return len([chunk for chunk in itertools.chain.from_iterable(self.chunks.values())])
    
    