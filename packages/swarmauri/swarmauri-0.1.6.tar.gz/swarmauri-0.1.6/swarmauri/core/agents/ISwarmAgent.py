from abc import ABC, abstractmethod
from typing import Any, Optional, List
from ..models.IModel import IModel
from ..toolkits.IToolkit import IToolkit
from ..parsers.IParser import IParser
from ..conversations.IConversation import IConversation
from ..documents.IDocument import IDocument
from ..retrievers.IRetriever import IRetriever
from ..messages.IMessage import IMessage

class ISwarmAgent(ABC):
    
    @abstractmethod
    def __init__(self, model: IModel, 
                 conversation: Optional[IConversation] = None, 
                 toolkit: Optional[IToolkit] = None, 
                 parser: Optional[IParser] = None, 
                 documents: Optional[List[IDocument]] = [], 
                 retriever: Optional[IRetriever] = None):
        pass
    
    @abstractmethod
    def exec(self, input_str: Optional[Any]) -> Any:
        pass
    
    @abstractmethod
    def get_model(self) -> IModel:
        """Returns the model component of the agent."""
        pass
    
    @abstractmethod
    def get_toolkit(self) -> Optional[IToolkit]:
        """Returns the toolkit component of the agent, if available."""
        pass
    
    @abstractmethod
    def get_parser(self) -> Optional[IParser]:
        """Returns the parser component of the agent, if available."""
        pass

    @abstractmethod
    def get_conversation(self) -> Optional[IConversation]:
        """Returns the conversation manager component of the agent, if available."""
        pass
    
    @abstractmethod
    def get_documents(self) -> List[IDocument]:
        """Returns the list of document components associated with the agent."""
        pass
    
    @abstractmethod
    def get_retriever(self) -> Optional[IRetriever]:
        """Returns the retriever component of the agent, if available."""
        pass

