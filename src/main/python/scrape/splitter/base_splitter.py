from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List

# Define type variables
T = TypeVar('T')  # Input type
U = TypeVar('U')  # Output type


class BaseSplitter(ABC, Generic[T, U]):
    @abstractmethod
    def split(self, input_data: T) -> List[U]:
        pass
