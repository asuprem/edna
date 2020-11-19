from __future__ import annotations
from typing import List
from collections import deque
from edna.types.builtin import StreamRecord


class RecordCollection(deque[StreamRecord]):
    def __init__(self,stream_records:List[StreamRecord]=[]):
        super().__init__(stream_records)

