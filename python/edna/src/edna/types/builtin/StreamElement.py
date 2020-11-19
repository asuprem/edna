from __future__ import annotations

from edna.types.enums import StreamElementType
import time

class StreamElement:
    """An element in a DataStream
    """
    elementType: StreamElementType
    eventTime: int
    def __init__(self, elementType: StreamElementType):
        self.eventTime = time.time()
        self.elementType = elementType

    def isRecord(self):
        return self.elementType == StreamElementType.RECORD
    
    def isCheckpoint(self):
        return self.elementType == StreamElementType.CHECKPOINT

    def getEventTime(self):
        return self.eventTime
