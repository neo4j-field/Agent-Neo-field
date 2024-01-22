import abc
from abc import ABC, abstractmethod, abstractproperty
from typing import Any, List

class BaseFetcher(ABC):
    def __init__(self):
        self._storage_client = None
        self._secret_manager_client = None

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