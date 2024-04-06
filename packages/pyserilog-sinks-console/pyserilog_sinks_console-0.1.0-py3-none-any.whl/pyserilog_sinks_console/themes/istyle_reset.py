from abc import ABC, abstractmethod


class IStyleReset(ABC):

    def __enter__(self):
        return self

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
