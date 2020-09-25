from edna.serializers import Serializable
from edna.process import BaseProcess
from edna.emit import BaseEmit
from edna.ingest import BaseIngest
from edna.serializers import Serializable

from edna.core.types.enums import IngestPattern

class StreamingIngestBase(BaseIngest):
    """StreamingIngest is the base class for obtaining records from a streaming source.
    
    Any edna.ingest function that inherits from StreamingIngest implements the stream() function.
    """    
    execution_mode = IngestPattern.SERVER_SIDE_STREAM
    def __init__(self, serializer: Serializable):
        super().__init__(serializer=serializer)

    def __call__(self, process: BaseProcess, emitter: BaseEmit):
        self.stream(process, emitter)

    def stream(self, process: BaseProcess, emitter: BaseEmit):
        raise NotImplementedError

from .TwitterIngestBase import TwitterIngestBase
from .TwitterFilterIngest import TwitterFilterIngest
from .TwitterStreamIngest import TwitterStreamIngest