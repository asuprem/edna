import enum

class BufferMode(enum.Enum):
    """Sets the mode for a edna.buffer.ByteBuffer.

    Args:
        enum ([type]): [description]
    """
    READ=1, 'Sets the ByteBuffer to READ mode.'
    WRITE=2, 'Sets the ByteBuffer to WRITE mode.'
    AVAILABLE=3, 'Sets the ByteBuffer to AVAILABLE mode.'