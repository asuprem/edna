from edna.serializers import Serializable
from edna.process import BaseProcess
from edna.emit import BaseEmit
from edna.ingest import BaseIngest
from edna.serializers import Serializable

from typing import Iterator

class IterableIngestBase(BaseIngest, Iterator):
    """IterableIngest is the base class for generating iterable records from a streaming source, e.g. Kafka.
    
    Any eednabka.ingest function that inherits from BaseIngest must implement the next() function.
    """    
    def __init__(self, serializer: Serializable):
        super().__init__(serializer)
    
    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        raise NotImplementedError

