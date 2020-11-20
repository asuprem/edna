from __future__ import annotations

from edna.serializers import MsgPackBufferedSerializer
from edna.types.enums import BufferMode
from edna.buffer import ByteBuffer
from edna.types.enums import EmitPattern
from typing import Dict
from edna.emit import BaseEmit

from typing import Dict
import socket
from typing import List

class _BufferedEmit(BaseEmit):
    """This emit writes to a network buffer to perform inter-task communication.
    
    Attributes:
        buffer (ByteBuffer): The internal network buffer. 
    """
    buffer: ByteBuffer

    def __init__(self, serializer: MsgPackBufferedSerializer = MsgPackBufferedSerializer(), 
        emit_buffer_batch_size: int = 10, emit_buffer_timeout_ms: int = 100, *args, **kwargs):
        """Initializes the emit.

        Args:
            serializer (MsgPackBufferedSerializer): The serializer for this emit.
            emit_buffer_batch_size (int, optional): How many records to emit at a time. Emit will collect 
                records until it has at least `emit_batch` records, then perform a write. 
                TODO Update this to byte size, instead. Defaults to 10.
            emit_buffer_timeout_ms (int, optional): How many ms to wait before emitting. This is to prevent 
                blocking on an unfilled buffer if incoming stream is slow. Defaults to 100.
        """
        super().__init__(serializer=serializer, 
            emit_buffer_batch_size=emit_buffer_batch_size,
            emit_buffer_timeout_ms=emit_buffer_timeout_ms, 
            logger_name=self.__class__.__name__,
            *args, **kwargs)
        self.emit_pattern = EmitPattern.BUFFERED_EMIT
        self.buffer = None

    def buildEmit(self, build_configuration: Dict[str, str]):
        """Builds the internal network buffer for the emitter.

        Args:
            build_configuration (Dict[str, str]): A build configuration containing host `ip`, 
                `emit_port`, `max_buffer_size` in bytes, and `max_buffer_timeout`
        """
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sender.connect((build_configuration["ip"], build_configuration["emit_port"]))
        self.buffer = ByteBuffer(self.sender, build_configuration["max_buffer_size"], build_configuration["max_buffer_timeout"], buffer_mode=BufferMode.WRITE)

    def write(self):
        """Writes the internal emit buffer to the network buffer.
        """
        for buffer_idx in range(self.emit_buffer_index+1):
            self.buffer.write(self.emit_buffer[buffer_idx])
        self.buffer.sendBufferAndReset()    # TODO handle this in a more elegant manner, re have buffer handle it itself on separate thread
        # Or this is the correct method -- we trigger the send becase write is triggered, which happens only when there is a timeout...

    def shutdownEmit(self):
        """Shuts down the emit, closing any connections if needed.
        """
        self.sender.close()