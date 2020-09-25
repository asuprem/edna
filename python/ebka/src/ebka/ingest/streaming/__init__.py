from ebka.serializers import Serializable
from ebka.process import BaseProcess
from ebka.emit import BaseEmit
from ebka.ingest import BaseIngest
from ebka.serializers import Serializable

class StreamingIngestBase(BaseIngest):
    """StreamingIngest is the base class for obtaining records from a streaming source.
    
    Any ebka.ingest function that inherits from StreamingIngest implements the stream() function.
    """    
    def __init__(self, serializer: Serializable):
        super().__init__(serializer=serializer)

    def __call__(self, process: BaseProcess, emitter: BaseEmit):
        self.stream(process, emitter)

    def stream(self, process: BaseProcess, emitter: BaseEmit):
        raise NotImplementedError

from .TwitterIngestBase import TwitterIngestBase
from .TwitterFilterIngest import TwitterFilterIngest
from .TwitterStreamIngest import TwitterStreamIngest