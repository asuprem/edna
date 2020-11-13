import enum

class SingleOutputStreamGraphNodeType(enum.Enum):
    """Enum to determine which type of Node this SingleOutputStreamGraphNode is.

    An INGEST node wraps an ingest primitive.

    A PROCESS node wraps an process primitive.

    An EMIT node wraps an emit primitive.
    """
    INGEST = 1
    PROCESS = 2
    EMIT = 3