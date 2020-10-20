from abc import abstractmethod
from edna.serializers import Serializable


class BufferedSerializable(Serializable):
    """Interface for a BufferedSerializable. A BufferedSerializable 

    Args:
        Serializable ([type]): [description]

    Raises:
        NotImplementedError: Raised if `feed()` or `__next__` are not implemented.
        NotImplementedError: [description]
    """
    def __init__(self):
        raise NotImplementedError

    def feed(self, buffered_message: bytes):
        raise NotImplementedError

    def __next__(self):
        return self.next()

    def next(self):
        raise NotImplementedError

    

    