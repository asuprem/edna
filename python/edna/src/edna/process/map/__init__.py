from __future__ import annotations
from typing import List
import warnings
from edna.process import BaseProcess
from edna.types.builtin import StreamRecord


class Map(BaseProcess):
    """A Map Process converts from one type to another. 

    Any child class must:
    
    - Implement the `map()` method
    
    - Call `super().__init__()` at the end of initialization
    
    Child classes should NOT:

    - modify the `process()` method


    Args:
        BaseProcess (BaseProcess): A process to chain
    """
    process_name : str = "Map"
    def __init__(self, process: BaseProcess = None, *args, **kwargs) -> BaseProcess:
        """Initializes the Process primitive. It can take a Process primitive as input to chain them.

        Args:
            process (BaseProcess, optional): A process primitive for functional chaining.

        Returns:
            BaseProcess: A chained process primitive.
        """
        super().__init__(process=process,  *args, **kwargs)
    
    def process(self, record: object) -> List[StreamRecord]:
        """This is the entrypoint to this primitive to map a record. It is called by the BaseProcess parent
        from the `__call__()` method. It subsequently calls the `map()` method.

        This should NOT be modified.

        Args:
            record (obj): A record to process with this primitive

        Returns:
            (List[obj]): A processed record in a singleton list.
        """
        return [StreamRecord(self.map(record))]

    def map(self, record: object) -> object:
        """Logic for mapping. Subclasses need to implement this.

        Args:
            record (obj): The record to process with this mapping logic

        Returns:
            (obj): A processed record
        """
        raise NotImplementedError()

from .JsonToObject import JsonToObject
from .ObjectToSQL import ObjectToSQL
from .ObjectToJson import ObjectToJson
from .KeyedSelect import KeyedSelect

SklearnClassifier = None
try:
    from .SklearnClassifier import SklearnClassifier
except (ImportError, AttributeError):
    warnings.warn("scikit-learn module is not installed. edna.process.map.SklearnClassifier might not work properly.", category=ImportWarning)
