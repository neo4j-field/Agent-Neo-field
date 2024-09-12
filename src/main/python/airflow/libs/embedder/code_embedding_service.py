from abc import ABC, abstractmethod
from typing import Any, Dict, List


class CodeEmbeddingService(ABC):
    @abstractmethod
    def embed_code(self, code_chunks: List[str]) -> List[Dict[str, Any]]:
        pass
