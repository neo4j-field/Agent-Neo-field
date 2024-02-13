from abc import ABC, abstractmethod
from typing import List, Dict

class CodeEmbeddingService(ABC):
    @abstractmethod
    def embed_code(self, code_chunks: List[str]) -> List[Dict[str, Any]]:
        pass