from __future__ import annotations
from typing import List
from edna.process import BaseProcess
from edna.process.map import Map

class KeyedSelect(Map):
    """Returns subset of dictionary

    Args:
        Map (BaseProcess): The interface this process implements
    """
    process_name : str = "KeyedSelect"

    def __init__(self, 
        keys = List[str],
        process: BaseProcess = None, 
        *args, **kwargs) -> BaseProcess:
        self.keys = keys
    def map(self, record: str):
        return {key:record[key] for key in self.keys}