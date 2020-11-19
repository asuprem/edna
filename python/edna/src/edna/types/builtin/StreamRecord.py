from __future__ import annotations
from edna.types.builtin import StreamElement
from edna.types.enums import StreamElementType


class StreamRecord(StreamElement):
    value: object

    def __init__(self, value: object):
        super().__init__(StreamElementType.RECORD)
        self.value = value

    def getValue(self):
        return self.value

    
