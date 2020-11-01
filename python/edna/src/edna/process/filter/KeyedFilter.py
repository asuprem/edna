from typing import Callable
from edna.process.filter import Filter
from edna.process import BaseProcess


class KeyedFilter(Filter):
    """Removes values.

    Args:
        Filter (BaseProcess): The interface this process implements
    """
    process_name : str = "KeyedFilter"
    # filter_callable  -->  boolean that takes in a value and returns true if it is to be removed
    def __init__(self, 
            key: str,
            filter_callable: Callable,
            process: BaseProcess = None, 
            *args, **kwargs):
        super().__init__(process=process, *args, **kwargs)
        self.key = key
        self.filter_callable = filter_callable
    
    def filter(self, message: str):
        return [message] if self.filter_callable(message[self.key]) else []