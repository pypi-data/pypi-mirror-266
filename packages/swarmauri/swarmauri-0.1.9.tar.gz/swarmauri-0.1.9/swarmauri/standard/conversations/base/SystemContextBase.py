from abc import ABC, abstractmethod
from typing import Optional, Union
from ....core.messages.IMessage import IMessage
from ....core.conversations.ISystemContext import ISystemContext
from ...messages.concrete.SystemMessage import SystemMessage

class SystemContextBase(ISystemContext, ABC):
    def __init__(self, *args, system_message_content: Optional[SystemMessage] = None):
        # Automatically handle both string and SystemMessage types for initializing system context
        self._system_context = None  # Initialize with None
        if system_message_content:
            self.system_context = system_message_content
    
    @property
    def system_context(self) -> Union[SystemMessage, None]:
        """Get the system context message. Raises an error if it's not set."""
        if self._system_context is None:
            raise ValueError("System context has not been set.")
        return self._system_context
    
    @system_context.setter
    def system_context(self, new_system_message: Union[SystemMessage, str]) -> None:
        """
        Set a new system context message. The new system message can be a string or 
        an instance of SystemMessage. If it's a string, it converts it to a SystemMessage.
        """
        if isinstance(new_system_message, SystemMessage):
            self._system_context = new_system_message
        elif isinstance(new_system_message, str):
            self._system_context = SystemMessage(new_system_message)
        else:
            raise ValueError("System context must be a string or a SystemMessage instance.")