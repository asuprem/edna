from typing import Callable
from edna.process.flatten import Flatten
from edna.process import BaseProcess


class StringFlatten(Flatten):
    """Removes values.

    Args:
        Flatten (BaseProcess): The interface this process implements
    """
    process_name : str = "StringFlatten"
    def __init__(self, 
            separator: str,
            process: BaseProcess = None, 
            *args, **kwargs):
        super().__init__(process=process, *args, **kwargs)
        self.separator = separator
    
    def flatten(self, message: str):
        return message.split(self.separator)