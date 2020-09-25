from ebka.serializers import Serializable
from ebka.process import BaseProcess
from ebka.emit import BaseEmit
from ebka.ingest import BaseIngest
from ebka.serializers import Serializable

from typing import Iterator

class IterableIngestBase(BaseIngest, Iterator):
    """IterableIngest is the base class for generating iterable records from a streaming source, e.g. Kafka.
    
    Any ebka.ingest function that inherits from BaseIngest must implement the next() function.
    """    
    def __init__(self, serializer: Serializable):
        super().__init__(serializer)
    
    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        raise NotImplementedError

