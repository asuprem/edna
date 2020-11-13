from abc import ABCMeta, abstractmethod

class Serializable:
    """Interface for Serialization.    
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def read(cls, in_stream: bytes): 
        """Convert from bytes to Serializable

        Args:
            in_stream (bytes): Input of bytes to deserialize
        """
        raise NotImplementedError
    @abstractmethod
    def write(cls, out_stream): 
        """Convert from Serializable to bytes

        Args:
            in_stream (Object): Input of Serializable to serialize
        """
        raise NotImplementedError

from .StringSerializer import StringSerializer
from .KafkaStringSerializer import KafkaStringSerializer
from .BufferedSerializable import BufferedSerializable
from .MsgPackBufferedSerializable import MsgPackBufferedSerializer