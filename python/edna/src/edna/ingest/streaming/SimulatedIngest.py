from edna.serializers import Serializable
from edna.ingest.streaming import BaseStreamingIngest

from typing import Callable, Dict, List
from time import sleep
import warnings

class SimulatedIngestCallable:
    """SimulatedIngestCallable is the interface for any Callable used in a SimulatedIngest. 

    Child classes should:
    
    - Implement the `compute_stream` method to return a stream element given an index value
    
    - Call `super().__init__()` if the interface constructor is overwritten

    Child classes should NOT:

    - Modify the `__call__` method
    """
    def __init__(self):
        """Empty base constructor """
        pass
    def __call__(self, index: int):
        """Calls the `compute_stream` method of the class

        Args:
            index (int): An integer passed by SimulatedIngest

        Returns:
            (obj): A generated record.
        """
        return self.compute_stream(index)
    def compute_stream(self, index):
        """This method needs to be implemented for any subclass.

        Args:
            index (int): An integer passed by SimulatedIngest

        Raises:
            NotImplementedError: Raise if child class does not implement this method.
        """
        raise NotImplementedError()

    def hasNext(self, index) -> bool:
        """Return True if there is still elements left to yield

        Args:
            index ([type]): [description]

        Raises:
            RuntimeError: [description]

        Returns:
            [type]: [description]
        """
        raise NotImplementedError()


class SimulatedIngest(BaseStreamingIngest):
    """The SimulatedIngest is used for testing EDNA Jobs. 
    Given a list of Serializable items, it will provide them when `__next__()` is called.
    """
    def __init__(self, stream_list: List = None, stream_callback: SimulatedIngestCallable = None, serializer: Serializable = None, *args, **kwargs):
        """Initialized the SimulatedIngest by recording the `stream_list` and preparing to emit them.

        Args:
            serializer (Serializable): Serializer to convert a record if needed.
            stream_list (List): List of stream elements to emit. Can be omitted if a 
                callable is used Defaults to None.
            stream_callback (Callable): A callback to generate new elements based on the index.
        """

        if stream_list is None and stream_callback is None:
            raise RuntimeError("Neither stream_callback not stream_list passed into SimulatedIngest. At least one needs to be passed.")
        if stream_list is not None:
            if stream_callback is not None:
                warnings.warn("Both stream_list and stream_callback have been passed. Defaulting to stream_list")
            self.stream_callback = self._ListCallable(stream_list)
        if stream_list is None and stream_callback is not None:
            self.stream_callback = stream_callback
        self.index = -1 # Because we need to increment the index before returning the value
        self.hasnext = True
        super().__init__(serializer=serializer, *args, **kwargs)

    def next(self):
        """Yields records from `self.stream_list` based on the current index. 

        Returns:
            (obj): A record.
        """
        self.index+=1
        return_val = self.stream_callback(self.index)
        if not self.stream_callback.hasNext(self.index+1):
            self.hasnext = False
        return return_val
    
    def hasNext(self) -> bool:
        return self.hasnext

    class _ListCallable(SimulatedIngestCallable):
        def __init__(self, stream_list: List):
            """This internal class implements a ListCallable -- basically a very thin wrapper around a python List.

            Args:
                stream_list (List): A list of records passed by `SimulatedIngest`
            """
            self.stream_list = stream_list
            self.max_index = len(self.stream_list)
            super().__init__()
        def compute_stream(self, index):
            """Yields records from `self.stream_list` based on the current index. Once the list is exhausted,
                `SimulatedIngest` blocks. TODO transition to internal sockeets between primitives to avoid blocking?.

            Args:
                index (int): An integer passed by SimulatedIngest

            Returns:
                (obj): A record from `stream_list`
            """
            
            return self.stream_list[index]

        def hasNext(self, index) -> bool:
            return index < self.max_index



__pdoc__ = {}
__pdoc__["SimulatedIngestCallable.__call__"] = True