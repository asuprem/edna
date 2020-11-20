from __future__ import annotations
from typing import Dict
from edna.serializers import Serializable
from edna.ingest import BaseIngest
from edna.serializers import Serializable
from edna.types.enums import IngestPattern
from edna.types.builtin import StreamRecord, RecordCollection
from typing import Iterator

class BaseStreamingIngest(BaseIngest, Iterator):
    """BaseStreamingIngest is the base class for generating records from a streaming source, e.g. Kafka.
    
    Any child class must:

    - Call `super().__init__()` at the end of initialization
    
    - Implement the `next()` method. This should be done as a generator that 
            fetches records in the background and yields them when it is called.
    
    Child classes should NOT:

    - modify the `__call__()` method
    
    - modify the `__iter__()` method

    Attributes:
        execution_mode (IngestPattern): The type of ingest, either STANDARD_INGEST or BUFFERED_INGEST
    """    
    execution_mode = IngestPattern.STANDARD_INGEST
    def __init__(self, serializer: Serializable = None, in_serializer: Serializable = None, out_serializer: Serializable = None, logger_name: str = None, *args, **kwargs):
        """Initialize the primitive with the serializer.

        Args:
            serializer (Serializable): Serializer for deserialize the streaming records.
        """
        if logger_name is None:
            logger_name = self.__class__.__name__
        super().__init__(serializer, in_serializer, out_serializer, logger_name, *args, **kwargs)
    
    def __iter__(self):
        """Returns itself as the iterator.

        Returns:
            (Iterator) : The class as an iterator.
        """
        return self

    def __next__(self) -> RecordCollection[StreamRecord]:
        """Fetches the next record from the source and deserializes

        Returns:
            (RecordCollection[StreamRecord]): Single fetched record in a singleton format.
        """
        return RecordCollection(
            [
                StreamRecord(self.in_serializer.read(self.next()))
                ]
        )

    def next(self) -> object:
        """Method that encapsulates raw record fetching logic.

        Raises:
            NotImplementedError: Child classes should implement this method.
        """
        raise NotImplementedError

    def build(self, build_configuration: Dict[str,str]):
        """Lazy building for ingest.
        """
        pass

    def close(self):
        """Shuts down the ingest, closing any connections if they exist
        """
        pass

from .TwitterStreamingIngest import TwitterStreamingIngest
from .TwitterFilteredIngest import TwitterFilteredIngest
from .KafkaIngest import KafkaIngest
from .SimulatedIngest import SimulatedIngest

__pdoc__ = {}
__pdoc__["BaseStreamingIngest.__iter__"] = True
__pdoc__["BaseStreamingIngest.__next__"] = True