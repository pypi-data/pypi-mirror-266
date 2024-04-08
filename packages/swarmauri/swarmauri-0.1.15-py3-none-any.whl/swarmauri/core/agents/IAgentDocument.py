from abc import ABC, abstractmethod
from swarmauri.core.documents.IDocument import IDocument

class IAgentDocumentStore(ABC):
    
    @property
    @abstractmethod
    def document_store(self) -> IDocument:
        pass

    @document_store.setter
    @abstractmethod
    def document_store(self) -> IDocument:
        pass