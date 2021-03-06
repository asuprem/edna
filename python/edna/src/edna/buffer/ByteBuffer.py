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

    def setName(self, name: str):
        """Attaches a suffix to the name if it is 'default'. Otherwise, returns the name itself.

        Args:
            name (str): Tentative name of this `ByteBuffer`.

        Returns:
            (str): The name for this `ByteBuffer`.
        """
        if name == EdnaDefault.BUFFER_NAME:
            return NameUtils.attachNameSuffix(name, suffix_length=5)
        return name

    def computeOverflow(self, message_length: int):
        """Compute the overflow of provided message length given the current 
        internal buffer size and the `MAX_BUFFER_SIZE`. The overflow is how
        much of the message will not fit into the current buffer because of
        `MAX_BUFFER_SIZE`

        Args:
            message_length (int): The length of the current message (in bytes).

        Returns:
            (int): Overflow of message in internal buffer. 
        """
        return self.buffer.tell() + message_length - self.MAX_BUFFER_SIZE

    def computeWriteIndex(self, message_length: int, overflow: int):
        """Compute how much of the message to write given the message lenth and
        overflow, the latter obtained from `computeOverflow()`. In case of 0 overflow,
        the entire message can be written into the buffer.

        Args:
            message_length (int): Length of message
            overflow (int): Message overflow, obtained from `computeOverflow`

        Returns:
            (int): Index up to which current message can be written into buffer. Returns length of message
                if overflow is 0.
        """
        write_index = message_length # This is how much of the message we will write
        if overflow >= 0:   # Add =0 for consistency
            write_index = message_length - overflow
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
        self.reset_buffer()

    def resetBuffer(self):
        """Reset the contents of the internal buffer
        """
        self.buffer = io.BytesIO()

    def addStragglers(self, message: bytes, message_length: int, write_length: int):
        """Adds the remaining contents of a message after a buffer reset in 
        case of overflow due to lalrge message.

        Args:
            message (bytes): The full message.
            message_length (int): The length of the message
            write_length (int): The message write index to write from. This is obtained from `computeWriteIndex`
        """
        if write_length < message_length:
            self.buffer.write(message[write_length:])


    def write(self, message: bytes):
        """Writes a given message into the internal buffer. If the messaage is too large to fit
        into the current buffer, `write()` will ad as much of the message as possible to the buffer,
        emit the buffer to the provided socket, reset, and fill it with the rest of the message.

        Args:
            message (bytes): The message to write to the buffer.
        """
        # TODO for java, add a reentrant lock here
        message_length = len(message)
        overflow = self.computeOverflow(message_length=message_length)
        write_length = self.computeWriteIndex(message_length=message_length, overflow=overflow)
        # Write to buffer main message
        self.buffer.write(message[:write_length])

        if self.buffer.tell() == self.MAX_BUFFER_SIZE:
            self.send_buffer_and_reset()
        
        self.addStragglers(message, message_length, write_length)