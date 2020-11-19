import enum

class StreamElementType(enum.Enum):
    """Enum to determine what type of StreamElement it is.

    A RECORD is a streaming record.

    A CHECKPOINT tells each process to back-up its state.
    """
    RECORD = 1
    CHECKPOINT = 2