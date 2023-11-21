from abc import ABC, abstractmethod


# TODO : I need to think about what this shared contract might look like.
class BaseFetcher(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def fetch_data(self):
        pass
