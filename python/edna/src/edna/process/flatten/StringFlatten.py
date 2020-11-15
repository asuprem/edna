from __future__ import annotations
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
    
    def flatten(self, message: str) -> List[str]:
        """Flattens a record using the separator and python's string `split()`.

        Args:
            message (str): A record to flatten.

        Returns:
            List[str]: An array of tokenized strings
        """
        return message.split(self.separator)