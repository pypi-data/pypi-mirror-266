from typing import Any, Optional, List

from ....core.models.IModel import IModel
from ....core.toolkits.IToolkit import IToolkit
from ....core.parsers.IParser import IParser
from ....core.conversations.IConversation import IConversation
from ....core.documents.IDocument import IDocument
from ....core.retrievers.IRetriever import IRetriever
from ....core.messages import IMessage

from ..base.SwarmAgentBase import SwarmAgentBase
from ...messages.concrete import HumanMessage

class SimpleSwarmAgent(SwarmAgentBase):
    def __init__(self, model: IModel, 
                 conversation: Optional[IConversation] = None, 
                 toolkit: Optional[IToolkit] = None, 
                 parser: Optional[IParser] = None, 
                 documents: Optional[List[IDocument]] = None, 
                 retriever: Optional[IRetriever] = None):
        super().__init__(model, conversation, toolkit, parser, documents, retriever)

    def exec(self, input_str: Optional[str] = None) -> Any:
        conversation = self.get_conversation()
        model = self.get_model()

        # Construct a new human message (for example purposes)
        if input_str:
            human_message = HumanMessage(input_str)
            conversation.add_message(human_message)
        
        messages = conversation.as_dict()
        prediction = model.predict(messages=messages)
        return prediction