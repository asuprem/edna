from edna.serializers import Serializable

class BaseEmit(object):
    """BaseEmit is the base class for writing records from a process primitive to a sink, 
    such as a filestream, sql database, or Kafka topic.

    Any child class must:

    - Implement the `write()` method

    - Call `super().__init__()` at the end of initialization
    
    Child classes should NOT:

    - modify the `__call__()` method

    """  
    def __init__(self, serializer: Serializable, *args, **kwargs):
        """Initializes the BaseEmit. This must be called by any inheriting classes using `super().__init__()`

        Args:
            serializer (Serializable): Serializer to use during emitting a record.
        """
        self.serializer = serializer

    def __call__(self, message):
        """Wrapper for emitting a record using the emitter's logic. This is the entry point for emitting and should not be modified.

        Args:
            message (object): A message that should be Serializable to bytes with `serializer`
        """
        self.write(self.serializer.write(message))

    def write(self, message: bytes):        # For Java, need Emit to be a templated function for message type
        """Writes a serialized message. This should be implemented by inheriting classes to emit with the appropriate logic.

        Args:
            message (bytes): Byte-encoded message.

        Raises:
            NotImplementedError: `write()` needs to be implemented in inheriting subclasses.
        """
        raise NotImplementedError()

from .KafkaEmit import KafkaEmit
from .StdoutEmit import StdoutEmit

__pdoc__ = {}
__pdoc__["BaseEmit.__call__"] = True


