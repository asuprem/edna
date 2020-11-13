import enum

class IngestPattern(enum.Enum):
    """Determines the type of ingest.

    A BUFFERED_INGEST yields records from a network buffer. This is usually sent
    by a `edna.emit._BufferedEmit`.

    A STANDARD_INGEST yields records from some streaming source, such as a file, 
    an external source, or Kafka.
    """
    BUFFERED_INGEST = 1
    STANDARD_INGEST = 2