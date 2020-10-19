from edna.serializers import Serializable
import time
from typing import List

class BaseEmit(object):
    """BaseEmit is the base class for writing records from a process primitive to a sink, 
    such as a filestream, sql database, or Kafka topic.

    Any child class must:

    - Implement the `write()` method. The write method will write all messages in the `self.emit_buffer` variable.
        `self.emit_buffer` is a List of Serialized messages

    - Call `super().__init__()` at the end of initialization
    
    Child classes should NOT:

    - modify the `__call__()` method

    """  
    def __init__(self, serializer: Serializable, emit_buffer_batch_size: int = 10, emit_buffer_timeout_ms: int = 100, *args, **kwargs):
        """Initializes the BaseEmit. This must be called by any inheriting classes using `super().__init__()`

        Args:
            serializer (Serializable): Serializer to use during emitting a record.
            emit_batch_size (int): How many items to emit at a time. Emit will collect 
                records until it has at least `emit_batch` records, then perform a write. 
                TODO Update this to byte size, instead
            emit_timeout_ms (int): How many ms to wait before emitting. This is to prevent 
                blocking on unfilled `emit_batch` if incoming stream is slow.
        """
        self.serializer = serializer
        if emit_buffer_batch_size <= 0:
            raise ValueError("emit_buffer_batch_size must be positive; received {emit_buffer_batch_size}".format(emit_buffer_batch_size = emit_buffer_batch_size))
        self.emit_buffer_batch_size = emit_buffer_batch_size
        self.emit_buffer = [None]*self.emit_buffer_batch_size
        self.emit_buffer_timeout_s = float(emit_buffer_timeout_ms) / 1000.
        self.emit_buffer_index = -1
        self.timer = time.time()
        

    def __call__(self, message):
        """Wrapper for emitting a record using the emitter's logic. This is the entry point for emitting and should not be modified.

        Args:
            message (List[object]): A list of messagse that should be Serializable to bytes with `serializer`
        """
        for item in message:
            self.call(item)
        
    def call(self, message):
        self.emit_buffer_index += 1
        self.emit_buffer[self.emit_buffer_index] = self.serializer.write(message)
        # Write buffer and clear if throughput barriers are met
        if (time.time() - self.timer) > self.emit_buffer_timeout_s:    # Buffer timeout reached
            self.write_buffer()
        if self.emit_buffer_index+1 == self.emit_buffer_batch_size: # Buffer too large
            self.write_buffer()


    def write_buffer(self):
        """Calls `write()` to write the buffer and resets the buffer"""
        self.write()
        self.reset_buffer()
    
    def reset_buffer(self):
        """Resets the internal buffer."""
        self.emit_buffer_index = -1
        self.emit_buffer = [None]*self.emit_buffer_batch_size
        self.timer = time.time()


    def write(self):        # For Java, need Emit to be a templated function for message type
        """Writes serialized messages. This should be implemented by inheriting classes to emit with the appropriate logic.
        Subclasses will write messages in the `emit_buffer` of the class. 

        Subclasses will also need to handle cases where the `emit_buffer` is not full by checking with `self.emit_buffer_index`.

        Raises:
            NotImplementedError: `write()` needs to be implemented in inheriting subclasses.
        """
        raise NotImplementedError()

from .KafkaEmit import KafkaEmit
from .StdoutEmit import StdoutEmit
from .SQLEmit import SQLEmit
from .SQLUpsertEmit import SQLUpsertEmit

__pdoc__ = {}
__pdoc__["BaseEmit.__call__"] = True


