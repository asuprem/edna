from __future__ import annotations
from abc import abstractmethod
from typing import Any
from edna.serializers import Serializable


class BufferedSerializable(Serializable):
    """Interface for a BufferedSerializable. A BufferedSerializable writes and reads
    records from network buffers. It is an internal serializer used between task primitives
    for an edna job.

    Subclasses should:
    
        - Implement `__init__()` method
        - Implement the `feed()` method. `feed()` receives a `buffered_message`, which is 
            byte array from the network buffer. They array contains a list of records, 
            with possibly incomplete records since the network buffer has limited capacity.
            The deserializer should keep track of incomplete records and use the byte array to 
            complete existing incomplete message and store records in an internal buffer.
        - Implement the `next()` method. `next()` should yield a single record from the internal
            buffer. `next()` should follow the ingest order and yield records in FIFO fashion.
        - Implement the `write()` method. `write()` should serialize a record and return a byte array.
    """
    def __init__(self):
        """Initializes the serializer.
        """
        raise NotImplementedError

    def feed(self, buffered_message: bytes):
        """Updates internal record buffer with the `buffered_message`

        Args:
            buffered_message (bytes): A byte-array representation of records from a network stack.
        """
        raise NotImplementedError

    def __next__(self) -> object:
        """Iterates over the next record in the internal record buffer

        Returns:
            object: Yields a record
        """
        return self.next()

    def next(self) -> object:
        """Logic for deserializing a complete record and yielding it.

        Returns:
            object: Yields a record
        """
        raise NotImplementedError

    @abstractmethod
    def read(cls, in_stream: Any):
        """Returns the message because the subclasses are tightly coupled with the ingest and perform the deserialization with `next()`.

        Args:
            in_stream (Any): A deserialized record

        Returns:
            (Any): The deserialized record
        """
        return in_stream

    @abstractmethod
    def write(cls, out_stream: object): 
        """Convert an object to bytes

        Args:
            in_stream (object): Input to serialize
        """
        raise NotImplementedError



    

    