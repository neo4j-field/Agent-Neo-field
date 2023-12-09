from abc import ABC, abstractmethod
from typing import Any, List

class BaseFetcher(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def fetch(self, *args, **kwargs) -> Any:
        pass

    @staticmethod
    def concatenate_unique_ordered(*lists: List[Any]) -> List[Any]:
        seen = set()
        result = []
        for item in lists:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
