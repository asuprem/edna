from __future__ import annotations
from edna.types.builtin import StreamElement
from edna.types.enums import StreamElementType


class StreamRecord(StreamElement):
    

    def __init__(self, value: object):
        super().__init__(value, StreamElementType.RECORD, 1)

    def isRecord(self):
        return True

    

    
