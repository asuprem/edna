import enum

class StreamElementType(enum.Enum):
    """Enum to determine what type of StreamElement it is.

    A RECORD is a streaming record.

    A CHECKPOINT tells each process to back-up its state.

    A WATERMARK tells each process that it has received all records prior to the watermark's time

    A SHUTDOWN tells the process to flush its records as it is the last element in the stream.
    """
    RECORD = 1
    CHECKPOINT = 2
    WATERMARK = 3
    SHUTDOWN = 4