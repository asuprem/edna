from __future__ import annotations
from collections import deque


class RecordCollection(deque):
    def __init__(self,stream_records=[]):
        super().__init__(stream_records)

