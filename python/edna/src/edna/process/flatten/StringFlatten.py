from __future__ import annotations
from edna.types.builtin import StreamRecord
from typing import List
from edna.process.flatten import Flatten
from edna.process import BaseProcess


class StringFlatten(Flatten):
    """Tokenizes a string using a provided separator.
    """
    process_name : str = "StringFlatten"
    def __init__(self, 
            separator: str,
            process: BaseProcess = None, 
            *args, **kwargs):
        """Initializes the flattener with the provided string separator.

        Args:
            separator (str): A string to use to flatten records.
            process (BaseProcess, optional): A chained process. Defaults to None.
        """
        super().__init__(process=process, *args, **kwargs)
        self.separator = separator
    
    def flatten(self, record: str) -> List[StreamRecord]:
        """Flattens a record using the separator and python's string `split()`.

        Args:
            record (str): A record to flatten.

        Returns:
            List[str]: An array of tokenized strings
        """
        return list(map(StreamRecord, record.split(self.separator)))