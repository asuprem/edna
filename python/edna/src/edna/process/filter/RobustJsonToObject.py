from __future__ import annotations
from edna.process.filter import Filter
from edna.types.builtin import StreamRecord
import ujson

class RobustJsonToObject(Filter):
    """Maps a json formatted string to a Dictionary, and discard malformed jsons

    Args:
        Map (BaseProcess): The interface this process implements
    """
    process_name : str = "RobustJsonToObject"
    def filter(self, record: str):
        try:
            return [StreamRecord(ujson.loads(record))]
        except ValueError:
            return []