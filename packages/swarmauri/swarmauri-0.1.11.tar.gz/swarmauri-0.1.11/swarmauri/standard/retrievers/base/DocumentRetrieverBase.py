from abc import ABC, abstractmethod
from typing import List
from ....core.vector_stores.IVectorStore import IVectorStore
from ....core.document_stores.IDocumentStore import IDocumentStore
from ....core.retrievers.IRetriever import IRetriever
from ....core.documents.IDocument import IDocument

class DocumentRetrieverBase(IRetriever, ABC):
    """
    Abstract base class for Retriever implementations.
    
    This class provides the foundation for building retrievers that 
    can fetch relevant documents based on a query. It defines the basic
    structure and required methods that concrete subclasses should implement.
    """

    def __init__(self, document_store: IDocumentStore):
        """
        Initialize the RetrieverBase with a document store and a vector store.

        Args:
            document_store (IDocumentStore): An instance of a document store.
            vector_store (IVectorStore): An instance of a vector store.
        """
        self.document_store = document_store
        
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve the top_k most relevant documents based on the given query.
        
        Args:
            query (str): The query string used for document retrieval.
            top_k (int): The number of top relevant documents to retrieve.
        
        Returns:
            List[IDocument]: A list of the top_k most relevant documents.
        """
        pass