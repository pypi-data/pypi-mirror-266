# swarmauri/core/chunkers/__init__.py

from abc import ABC, abstractmethod
from typing import List, Union, Any

class IChunker(ABC):
    """
    Interface for chunking text into smaller pieces.

    This interface defines abstract methods for chunking texts. Implementing classes
    should provide concrete implementations for these methods tailored to their specific
    chunking algorithms.

    """
    
    @abstractmethod
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[str]:
        """
        Abstract method that splits a text into chunks.

        Parameters:
        - text (Union[str, Any]): The input text to be chunked. This can be a string 
                                  or any other format that the concrete implementation
                                  can handle.
        - *args: Variable length argument list. Allows for flexibility in arguments that
                 can be passed to implementing methods.
        - **kwargs: Arbitrary keyword arguments.
        
        Returns:
        - List[str]: A list of text chunks.
        """
        pass