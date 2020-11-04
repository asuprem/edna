import enum

class SingleOutputStreamGraphNodeProcessType(enum.Enum):
    """Enum to determine which type of Node this SingleOutputStreamGraphNode is.
    """
    MAP = 1
    FLATTEN = 2
    FILTER = 3