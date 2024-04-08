from abc import ABC, abstractmethod
from typing import Dict

class IEmbed(ABC):
    @abstractmethod
    def __init__(self, doc_id, content, metadata: Dict):
        pass

    @property
    @abstractmethod
    def embedding(self) -> str:
        """
        Get the document's ID.
        """
        pass

    @embedding.setter
    @abstractmethod
    def embedding(self, value: str) -> None:
        """
        Set the document's ID.
        """
        pass

