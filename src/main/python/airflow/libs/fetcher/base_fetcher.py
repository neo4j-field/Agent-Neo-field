from abc import ABC, abstractmethod
from typing import Any, List


class BaseFetcher(ABC):
    def __init__(self, storage_client=None, secret_client=None):
        self._storage_client = storage_client
        self._secret_manager_client = secret_client

    @abstractmethod
    def storage_client(self):
        pass

    @abstractmethod
    def secret_manager_client(self):
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
