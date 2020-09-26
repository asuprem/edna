from edna.serializers import Serializable
from edna.process import BaseProcess
from edna.emit import BaseEmit
from edna.ingest import BaseIngest
from edna.serializers import Serializable

from edna.core.types.enums import IngestPattern

from typing import Iterator

class BaseStreamingIngest(BaseIngest, Iterator):
    """BaseStreamingIngest is the base class for generating records from a streaming source, e.g. Kafka.
    
    Any edna.ingest function that inherits from BaseStreamingIngest must implement the next() function.
    """    
    execution_mode = IngestPattern.CLIENT_SIDE_STREAM
    def __init__(self, serializer: Serializable):
        super().__init__(serializer)
    
    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        raise NotImplementedError

from .TwitterStreamingIngest import TwitterStreamingIngest
from .TwitterFilteredIngest import TwitterFilteredIngest