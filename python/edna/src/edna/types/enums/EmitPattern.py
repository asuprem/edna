import enum

class EmitPattern(enum.Enum):
    """Determines the type of emit.

    A BUFFERED_EMIT writes records to a network buffer. This is usually sent
    to a `edna.emit._BufferedIngest`.

    A STANDARD_EMIT writes records to a sink, such as a file, an external database, 
    or Kafka.
    """
    BUFFERED_EMIT = 1
    STANDARD_EMIT = 2