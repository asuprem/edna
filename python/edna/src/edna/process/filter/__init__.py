from __future__ import annotations
from edna.types.builtin import StreamRecord
from typing import List
from edna.process import BaseProcess


class Filter(BaseProcess):
    """A Filter Process filters the input. 

    Any child class must:
    
    - Implement the `filter()` method
    
    - Call `super().__init__()` at the end of initialization
    
    Child classes should NOT:

    - modify the `process()` method


    Args:
        BaseProcess (BaseProcess): A process to chain
    """
    process_name : str = "Filter"
    def __init__(self, process: BaseProcess = None, *args, **kwargs) -> BaseProcess:
        """Initializes the Process primitive. It can take a Process primitive as input to chain them.

        Args:
            process (BaseProcess, optional): A process primitive for functional chaining.

        Returns:
            BaseProcess: A chained process primitive.
        """
        super().__init__(process=process,  *args, **kwargs)
    
    def process(self, record: object) -> List[StreamRecord]:
        """This is the entrypoint to this primitive to filter a record. It is called by the BaseProcess parent
        from the `__call__()` method. It subsequently calls the `filter()` method.

        This should NOT be modified.

        Args:
            record (obj): A record to process with this primitive

        Returns:
            (List[obj]): A processed record in a singleton list.
        """
        return self.filter(record)

    def filter(self, record: object) -> List[StreamRecord]:
        """Logic for filtering. Subclasses need to implement this.

        Args:
            record (obj): The record to process with this filtering logic

        Returns:
            (List[StreamRecord]): A processed record as an array. Must be an array.
        """
        raise NotImplementedError()

from .KeyedFilter import KeyedFilter
from .RobustJsonToObject import RobustJsonToObject