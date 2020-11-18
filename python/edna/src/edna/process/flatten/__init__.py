from __future__ import annotations
from edna.process import BaseProcess

from typing import List


class Flatten(BaseProcess):
    """A Flatten Process takes a stream of collections and flattens them to a stream of records. 

    Any child class must:
    
    - Implement the `flatten()` method
    
    - Call `super().__init__()` at the end of initialization
    
    Child classes should NOT:

    - modify the `process()` method


    Args:
        BaseProcess (BaseProcess): A process to chain
    """
    process_name : str = "Flatten"
    def __init__(self, process: BaseProcess = None, *args, **kwargs) -> BaseProcess:
        """Initializes the Process primitive. It can take a Process primitive as input to chain them.

        Args:
            process (BaseProcess, optional): A process primitive for functional chaining.

        Returns:
            BaseProcess: A chained process primitive.
        """
        super().__init__(process=process,  *args, **kwargs)
    
    def process(self, record: List[object]) -> List[object]:
        """This is the entrypoint to this primitive to flatten a record. It is called by the BaseProcess parent
        from the `__call__()` method. It subsequently calls the `flatten()` method.

        This should NOT be modified.

        Args:record
            record (obj): A record to process with this primitive

        Returns:
            (List[obj]): A processed record in a singleton list.
        """
        return self.flatten(record)

    def flatten(self, record: List[object]) -> List[object]:
        """Logic for flattening. Subclasses need to implement this.

        Args:
            record (obj): The record to process with this flatenning logic

        Returns:
            (obj): A processed record as an array. Must be an array of records.
        """
        raise NotImplementedError()

from .StringFlatten import StringFlatten