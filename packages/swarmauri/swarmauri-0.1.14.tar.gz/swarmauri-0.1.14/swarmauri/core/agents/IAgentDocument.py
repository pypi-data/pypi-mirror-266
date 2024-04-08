from abc import ABC, abstractmethod
from swarmauri.core.documents.IDocument import IDocument

class IAgentDocument(ABC):
    
    @property
    @abstractmethod
    def documents(self) -> IDocument:
        pass

    @documents.setter
    @abstractmethod
    def documents(self) -> IDocument:
        pass