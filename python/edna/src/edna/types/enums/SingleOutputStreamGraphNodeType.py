import enum

class SingleOutputStreamGraphNodeType(enum.Enum):
    """Enum to determine which type of Node this SingleOutputStreamGraphNode is.
    """
    INGEST = 1
    PROCESS = 2
    EMIT = 3