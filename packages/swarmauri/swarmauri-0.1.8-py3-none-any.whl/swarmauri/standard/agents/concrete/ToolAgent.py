from typing import Any, Optional, List, Union, Dict
import json

from ....core.models.IModel import IModel
from ....core.toolkits.IToolkit import IToolkit
from ....core.parsers.IParser import IParser
from ....core.conversations.IConversation import IConversation
from ....core.documents.IDocument import IDocument
from ....core.retrievers.IRetriever import IRetriever
from ....core.messages import IMessage

from ..base.SwarmAgentBase import SwarmAgentBase
from ...messages.concrete import HumanMessage, AgentMessage, FunctionMessage


class ToolAgent(SwarmAgentBase):
    def __init__(self, 
                 model: IModel, 
                 conversation: Optional[IConversation] = None, 
                 toolkit: Optional[IToolkit] = None, 
                 parser: Optional[IParser] = None,
                 documents: Optional[List[IDocument]] = None, 
                 retriever: Optional[IDocument] = None):
        super().__init__(model, conversation, toolkit, parser, documents, retriever)

    def exec(self, input_data: Union[str, IMessage],  model_kwargs: Optional[Dict] = {}) -> Any:
        conversation = self.get_conversation()
        model = self.get_model()
        tools = self.get_toolkit()
        

        # Check if the input is a string, then wrap it in a HumanMessage
        if isinstance(input_data, str):
            human_message = HumanMessage(input_data)
        elif isinstance(input_data, IMessage):
            human_message = input_data
        else:
            raise TypeError("Input data must be a string or an instance of Message.")

        # Add the human message to the conversation
        conversation.add_message(human_message)

            
        
        # Retrieve the conversation history and predict a response
        messages = conversation.as_dict()
        
        prediction = model.predict(messages=messages, 
                                   tools=tools.tools, 
                                   tool_choice="auto", 
                                   **model_kwargs)
        
        prediction_message = prediction.choices[0].message
        
        agent_response = prediction_message.content
        
        agent_message = AgentMessage(content=prediction_message.content, 
                                     tool_calls=prediction_message.tool_calls)
        conversation.add_message(agent_message)
        
        tool_calls = prediction.choices[0].message.tool_calls
        if tool_calls:
        
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                
                func_call = self.toolkit.get_tool_by_name(func_name)
                func_args = json.loads(tool_call.function.arguments)
                func_result = func_call(**func_args)
                
                func_message = FunctionMessage(func_result, 
                                               name=func_name, 
                                               tool_call_id=tool_call.id)
                conversation.add_message(func_message)
            
            
            messages = conversation.as_dict()
            rag_prediction = model.predict(messages=messages, 
                                           tools=tools.tools, 
                                           tool_choice="none",
                                           **model_kwargs)
            
            prediction_message = rag_prediction.choices[0].message
            
            agent_response = prediction_message.content
            agent_message = AgentMessage(agent_response)
            conversation.add_message(agent_message)
            prediction = rag_prediction
            
        return agent_response 
    