from __future__ import annotations

from edna.serializers import Serializable
from typing import List
import logging

class EdnaPrimitive(object):
    """EdnaPrimitive is the root class for an edna primitive. It sets up logging and serializers for the Primitive.

    Attributes:
        logger (logging.Logger): The logger for the Primitive. Initialized with a provided name; if no name is provided,
            `logger` uses the class name.
        serializer (Serializable): A serializer for this Primitive. It can be used to serialize and deserialize
            records between processes.
        in_serializer (Serializable): A serializer that should be used when reading from the input stream.
        out_serializer (Serializable): A serializer that should be used when writing to the output stream.

    Raises:
        ValueError: Raised when a serializer is passed incorrectly
        NotImplementedError: Raised if `__call__()` or `__next__()` methods are called. These methods should be
            implemented in subclasses.
    """
    logger: logging.Logger
    serializer: Serializable
    in_serializer: Serializable
    out_serializer: Serializable

    def __init__(self, serializer: Serializable, 
            in_serializer: Serializable = None, 
            out_serializer: Serializable = None, 
            logger_name: str = None,
            *args, **kwargs):
        """Initializes the Primitive.

        Args:
            serializer (Serializable): A serializer for this Primitive. It can be used to serialize and deserialize
                records between processes. If not provided, then `in_serializer` and `out_serializer` must be provided.
            in_serializer (Serializable, optional): A serializer for this Primitive. It can be used when reading 
                from the input stream. Defaults to None.
            out_serializer (Serializable, optional): A serializer for this Primitive. It can be used when writing 
                to the output stream. Defaults to None.
            logger_name (str, optional): A name for this Primitive's `logger`. If no name is provided, `logger` uses 
                the class name. Defaults to None.

        Raises:
            ValueError: Raised when a serializer is passed incorrectly
        """

        self.serializer = serializer
        if self.serializer is None:
            if in_serializer is None:
                raise ValueError("`in_serializer` cannot be None if serializer is `None` for Primitive")
            if out_serializer is None:
                raise ValueError("`in_serializer` cannot be None if serializer is `None` for Primitive")
            self.in_serializer = in_serializer
            self.out_serializer = out_serializer
        else:
            self.in_serializer = self.serializer
            self.out_serializer = self.serializer

        if logger_name is None:
            self.logger = logging.getLogger(self.__class__.__name__)
        else:
            self.logger = logging.getLogger(logger_name)

    def __call__(self, record: List[object]) -> List[object]:
        """Used by edna.process and edna.emit primitives. When called, they will process and 
        emit records, respectively. 

        Args:
            record (List[object]): A list of records.

        Returns:
            List[object]: A list of processed records
        """
        raise NotImplementedError

    def __next__(self) -> List[object]:
        """Used by edna.emit. When called, it will yield records either as a source itself or 
        from a source.

        Returns:
            List[object]: A list of records from a source
        """
        raise NotImplementedError