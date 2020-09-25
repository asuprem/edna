import abc
from abc import ABCMeta, abstractmethod

class Serializable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def read(self, in_stream): raise NotImplementedError
    @abstractmethod
    def write(self, out_stream): raise NotImplementedError

