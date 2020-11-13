from edna.emit import BaseEmit
from edna.serializers import Serializable

from sys import stdout
import time

class RecordCounterEmit(BaseEmit):
    """An Emitter that counts the number of records"""
    def __init__(self, serializer: Serializable, record_print: int = 1000, emit_buffer_batch_size: int = 10, emit_buffer_timeout_ms: int = 100, *args, **kwargs):
        self.index = 0
        self.record_print = record_print
        self.record_timer = time.time()
        super().__init__(serializer=serializer, emit_buffer_batch_size=emit_buffer_batch_size,emit_buffer_timeout_ms=emit_buffer_timeout_ms, *args, **kwargs)
    def write(self):
        """Writes the message to the standard output. Ideally, the message should be a string. This is useful only for debugging."""
        # NOT an efficient method, but really, who uses this for a real Job?
        for buffer_idx in range(self.emit_buffer_index+1):
            if self.index % self.record_print == 0:
                pause = time.time() - self.record_timer
                print(self.index, pause, file=stdout)
            self.index+=1

        