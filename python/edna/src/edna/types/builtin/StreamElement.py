from __future__ import annotations

from edna.types.enums import StreamElementType
import time

class StreamElement:
    """An element in a DataStream
    """
    elementType: StreamElementType
    eventTime: int
    value: object
    elementTypeSecondary: int
    def __init__(self, value, elementType: StreamElementType, elementTypeSecondary: int):
        self.eventTime = time.time()
        self.elementType = elementType
        self.value = value
        self.elementTypeSecondary = elementTypeSecondary

    def isRecord(self):
        return False
    
    def isCheckpoint(self):
        return False

    def isWatermark(self):
        return False

    def isShutdown(self):
        return False

    def getEventTime(self):
        return self.eventTime

    def getValue(self) -> object:
        return self.value
