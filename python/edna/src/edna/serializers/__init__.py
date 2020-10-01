from abc import ABCMeta, abstractmethod

class Serializable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def read(self, in_stream: bytes): raise NotImplementedError
    @abstractmethod
    def write(self, out_stream): raise NotImplementedError

from .StringSerializer import StringSerializer