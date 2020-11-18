from __future__ import annotations

import io
import socket
from edna.types.enums import BufferMode
from edna.utils import NameUtils
from edna.defaults import EdnaDefault

class ByteBuffer:
    """A ByteBuffer is a wrapper around an `io.BytesIO()` buffer. EDNA uses the ByteBuffer to
    pass records in a local DAG.

    The ByteBuffer is initialized with a MAX_BUFFER_SIZE (defaults to 32KiB). When the internal
    buffer is filled, ByteBuffer will emit the contents to the provided socket, then reset the buffer
    to write additional records.
    """
    socket: socket.socket
    buffer: io.BytesIO
    name: str
    buffer_mode: BufferMode
    def __init__(self, socket: socket.socket, 
            max_buffer_size : int = EdnaDefault.BUFFER_MAX_SIZE, 
            max_buffer_timeout: float = EdnaDefault.BUFFER_MAX_TIMEOUT_S, 
            name: str = EdnaDefault.BUFFER_NAME,
            buffer_mode : BufferMode = BufferMode.READ):
        """Initializes the ByteBuffer.

        Args:
            socket (socket.socket): A socket object to write to. This socket should be initialized outside the class. 
                `ByteBuffer` will call the `send()` method for this socket object.
            max_buffer_size (int, optional): Maximum size of the ByteBuffer's internal buffer. Defaults to 2048.
            max_buffer_timeout (float, optional): Maximum time to wait for incomplete buffer before emitting it. 
                Unused for now. Defaults to 0.5.
            name (str, optional): Name for this ByteBuffer. Defaults to "default".
            buffer_mode (BufferMode, optional): An `edna.types.enums.BufferMode` for this ByteBuffer. 
                Defaults to BufferMode.READ.
        """
        self.MAX_BUFFER_SIZE = max_buffer_size
        self.MAX_BUFFER_TIMEOUT_S = max_buffer_timeout  # Unused for now...
        self.name = self.setName(name)
        self.buffer_mode = buffer_mode
        self.socket = socket

        self.reset()

    def setName(self, name: str) -> str:
        """Attaches a suffix to the name if it is 'default'. Otherwise, returns the name itself.

        Args:
            name (str): Tentative name of this `ByteBuffer`.

        Returns:
            str: The name for this `ByteBuffer`.
        """
        if name == EdnaDefault.BUFFER_NAME:
            return NameUtils.attachNameSuffix(name, suffix_length=5)
        return name

    def computeOverflow(self, record_length: int) -> int:
        """Compute the overflow of provided record length given the current 
        internal buffer size and the `MAX_BUFFER_SIZE`. The overflow is how
        much of the record will not fit into the current buffer because of
        `MAX_BUFFER_SIZE`

        Args:
            record_length (int): The length of the current record (in bytes).

        Returns:
            int: Overflow of record in internal buffer. 
        """
        return self.buffer.tell() + record_length - self.MAX_BUFFER_SIZE

    def computeWriteIndex(self, record_length: int, overflow: int) -> int:
        """Compute how much of the record to write given the record lenth and
        overflow, the latter obtained from `computeOverflow()`. In case of 0 overflow,
        the entire record can be written into the buffer.

        Args:
            record_length (int): Length of record
            overflow (int): Record overflow, obtained from `computeOverflow`

        Returns:
            int: Index up to which current record can be written into buffer. Returns length of record
                if overflow is 0.
        """
        write_index = record_length # This is how much of the record we will write
        if overflow >= 0:   # Add =0 for consistency
            write_index = record_length - overflow
        return write_index

    def sendBufferAndReset(self):
        """Sends the current contents of the buffer to the socket and reset it.
        """
        # TODO for java, add a reentrant lock here
        # First send the buffer contents
        if self.buffer.tell():  #i.e. if there is something in buffer
            self.socket.send(self.buffer.getvalue())
            self.reset()

    def reset(self):
        """Reset the ByteBuffer. TODO Timing reset might be added in the future here, if ByteBuffer is managed on another thread.
        """
        self.resetBuffer()

    def resetBuffer(self):
        """Reset the contents of the internal buffer
        """
        self.buffer = io.BytesIO()

    def addStragglers(self, record: bytes, record_length: int, write_length: int):
        """Adds the remaining contents of a record after a buffer reset in 
        case of overflow due to lalrge record.

        Args:
            record (bytes): The full record.
            record_length (int): The length of the record
            write_length (int): The record write index to write from. This is obtained from `computeWriteIndex`
        """
        if write_length < record:
            self.buffer.write(record[write_length:])


    def write(self, record: bytes):
        """Writes a given record into the internal buffer. If the messaage is too large to fit
        into the current buffer, `write()` will ad as much of the record as possible to the buffer,
        emit the buffer to the provided socket, reset, and fill it with the rest of the record.

        Args:
            record (bytes): The record to write to the buffer.
        """
        # TODO for java, add a reentrant lock here
        record_length = len(record)
        overflow = self.computeOverflow(record_length=record_length)
        write_length = self.computeWriteIndex(record_length=record_length, overflow=overflow)
        # Write to buffer main record
        self.buffer.write(record[:write_length])

        if self.buffer.tell() == self.MAX_BUFFER_SIZE:
            self.send_buffer_and_reset()
        
        self.addStragglers(record, record_length, write_length)