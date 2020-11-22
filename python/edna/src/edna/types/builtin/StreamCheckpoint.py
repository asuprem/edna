from __future__ import annotations
from edna.types.builtin import StreamElement
from edna.types.enums import StreamElementType


class StreamCheckpoint(StreamElement):
    def __init__(self):
        super().__init__(None, StreamElementType.CHECKPOINT, 2)

    
    def isCheckpoint(self):
        return True