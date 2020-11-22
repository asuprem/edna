from __future__ import annotations
from edna.types.builtin import StreamElement
from edna.types.enums import StreamElementType


class StreamWatermark(StreamElement):
    def __init__(self):
        super().__init__(None, StreamElementType.WATERMARK, 3)

    def isWatermark(self):
        return True

    
