from __future__ import annotations
from edna.types.builtin import StreamElement
from edna.types.enums import StreamElementType


class StreamShutdown(StreamElement):
    def __init__(self):
        super().__init__(None, StreamElementType.SHUTDOWN)

    def isShutdown(self):
        return True

    
