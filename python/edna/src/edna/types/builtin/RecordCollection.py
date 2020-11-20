from __future__ import annotations
from typing import List, Deque
from collections import deque
from edna.types.builtin import StreamRecord


class RecordCollection(Deque[StreamRecord]):
    def __init__(self,stream_records:List[StreamRecord]=[]):
        super().__init__(stream_records)

