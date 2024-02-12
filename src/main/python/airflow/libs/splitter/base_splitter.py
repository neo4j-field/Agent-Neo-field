from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List

# Define type variables
T = TypeVar('T')  # Input type
U = TypeVar('U')  # Output type


class BaseSplitter(ABC, Generic[T, U]):

    def __init__(self):
        self._storage_client = None
        self._secret_manager_client = None

    @abstractmethod
    def split(self, input_data: T, *args, **kwargs) -> List[U]:
        """
        Abstract method to be implemented by subclasses.

        :param input_data: The input data to split.
        :param args: Additional non-keyword arguments.
        :param kwargs: Additional keyword arguments.
        :return: A list of chunks of type U.
        """
        pass
