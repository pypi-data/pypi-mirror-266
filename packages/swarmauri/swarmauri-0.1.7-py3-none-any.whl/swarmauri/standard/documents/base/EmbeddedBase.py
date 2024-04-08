from abc import ABC
from typing import List, Any
from swarmauri.core.documents.IEmbed import IEmbed


class EmbeddedBase(IEmbed, ABC):
    def __init__(self, embedding):
        self._embedding = embedding
            
    @property
    def embedding(self) -> List[Any]:
        """
        Get the document's ID.
        """
        return self._embedding

    @embedding.setter
    def embedding(self, value: List[Any]) -> None:
        """
        Set the document's ID.
        """
        self._embedding = value