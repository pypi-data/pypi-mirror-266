from typing import Any, Optional, List, Union, Dict
from ....core.models.IModel import IModel
from ....core.toolkits.IToolkit import IToolkit
from ....core.parsers.IParser import IParser
from ....standard.conversations.concrete.SharedConversation import SharedConversation
from ....core.documents.IDocument import IDocument
from ....core.retrievers.IRetriever import IRetriever
from ....core.messages import IMessage

from ..base.SwarmAgentBase import SwarmAgentBase
from ...messages.concrete import HumanMessage, AgentMessage

class MultiPartyChatSwarmAgent(SwarmAgentBase):
    def __init__(self, 
                 model: IModel, 
                 conversation: Optional[SharedConversation] = None, 
                 toolkit: Optional[IToolkit] = None, 
                 parser: Optional[IParser] = None,
                 documents: Optional[List[IDocument]] = None, 
                 retriever: Optional[IRetriever] = None,
                 name: str = None):
        super().__init__(model, conversation, toolkit, parser, documents, retriever)
        self.name = name

    def exec(self, input_data: Union[str, IMessage] = "", model_kwargs: Optional[Dict] = {}) -> Any:
        conversation = self.get_conversation()
        model = self.get_model()

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")

        if input_data != "":
            # Add the human message to the conversation
            conversation.add_message(human_message, sender_id=self.name)
        
        # Retrieve the conversation history and predict a response
        messages = conversation.as_dict()

        
        if model_kwargs:
            prediction = model.predict(messages=messages, **model_kwargs)
        else:
            prediction = model.predict(messages=messages)
        # Create an AgentMessage instance with the model's response and update the conversation
        if prediction != '':
            agent_message = AgentMessage(prediction)
            conversation.add_message(agent_message, sender_id=self.name)
        
        return prediction