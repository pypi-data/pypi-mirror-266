from typing import Any, Optional, List
from abc import ABC, abstractmethod
from ....core.agents.ISwarmAgent import ISwarmAgent
from ....core.models.IModel import IModel
from ....core.toolkits.IToolkit import IToolkit
from ....core.parsers.IParser import IParser
from ....core.conversations.IConversation import IConversation
from ....core.documents.IDocument import IDocument
from ....core.retrievers.IRetriever import IRetriever
from ...messages.concrete.HumanMessage import HumanMessage

class SwarmAgentBase(ISwarmAgent, ABC):
    @abstractmethod
    def __init__(self, 
                 model: IModel, 
                 conversation: Optional[IConversation] = None,
                 toolkit: Optional[IToolkit] = None, parser: Optional[IParser] = None, 
                 documents: Optional[List[IDocument]] = [], retriever: Optional[IRetriever] = None):

        super().__init__(model, conversation, toolkit, parser, documents, retriever)
        self._model = model
        self._toolkit = toolkit
        self._parser = parser
        self._conversation = conversation
        self._documents = documents 
        self._retriever = retriever

    def exec(self, input_str: Optional[Any]) -> Any:
        pass
    
    @property
    def model(self) -> IModel:
        return self._model
    
    @model.setter
    def model(self, value) -> IModel:
        self._model = value        

    def get_model(self) -> IModel:
        return self._model
    
    def get_toolkit(self) -> Optional[IToolkit]:
        return self._toolkit
    
    @property
    def parser(self) -> IModel:
        return self._parser
    
    @model.setter
    def parser(self, value) -> IModel:
        self._parser = value
    
    
    def get_parser(self) -> Optional[IParser]:
        return self._parser

    @property
    def conversation(self) -> Optional[IConversation]:
        return self._conversation

    @conversation.setter
    def conversation(self, value) -> Optional[IConversation]:
        self._conversation = value

    def get_conversation(self) -> Optional[IConversation]:
        return self._conversation
    
    def get_documents(self) -> List[IDocument]:
        return self._documents
    
    def get_retriever(self) -> Optional[IRetriever]:
        return self._retriever 
    
    def __getattr__(self, name):
        # Example of transforming attribute name from simplified to internal naming convention
        internal_name = f"_{name}"
        if internal_name in self.__dict__:
            return self.__dict__[internal_name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        # Direct assignment to the __dict__ to bypass any potential infinite recursion
        # from setting attributes that do not explicitly exist.
        object.__setattr__(self, name, value) 
        
        
    def __str__(self):
        class_name = self.__class__.__name__
        variables_str = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"<{class_name} {variables_str}>"
        
    def __repr__(self):
        class_name = self.__class__.__name__
        variables_str = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{class_name} ({variables_str})"