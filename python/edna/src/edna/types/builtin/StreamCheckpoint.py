from __future__ import annotations
from edna.types.builtin import StreamElement
from edna.types.enums import StreamElementType


class StreamCheckpoint(StreamElement):
    def __init__(self):
        super().__init__(StreamElementType.CHECKPOINT)

    
