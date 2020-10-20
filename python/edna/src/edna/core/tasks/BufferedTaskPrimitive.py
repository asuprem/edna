from edna.core.tasks import TaskPrimitive
from edna.defaults import EdnaDefault
from edna.buffer import ByteBuffer
import time


class BufferedTaskPrimitive(TaskPrimitive):
    buffer: ByteBuffer
    def __init__(self, max_buffer_size : int = EdnaDefault.BUFFER_MAX_SIZE, 
            max_buffer_timeout : float = EdnaDefault.BUFFER_MAX_TIMEOUT_S):
        super().__init__(max_buffer_size=max_buffer_size, max_buffer_timeout=max_buffer_timeout)
        self.buffer = ByteBuffer(self.sender, max_buffer_size=self.MAX_BUFFER_SIZE, max_buffer_timeout=self.MAX_BUFFER_TIMEOUT_S)
         
    def checkBufferTimeout(self):
        if (time.time() - self.timer) > self.MAX_BUFFER_TIMEOUT_S:
            self.buffer.sendBufferAndReset()
            self.timer = time.time()