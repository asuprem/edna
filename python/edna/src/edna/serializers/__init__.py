from abc import ABCMeta, abstractmethod

class Serializable:
    """Interface for Serialization.    
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def read(self, in_stream: bytes): 
        """Convert from bytes to Serializable

        Args:
            in_stream (bytes): Input of bytes to deserialize
        """
        raise NotImplementedError
    @abstractmethod
    def write(self, out_stream): 
        """Convert from Serializable to bytes

        Args:
            in_stream (Object): Input of Serializable to serialize
        """
        raise NotImplementedError

from .StringSerializer import StringSerializer
from .KafkaStringSerializer import KafkaStringSerializer