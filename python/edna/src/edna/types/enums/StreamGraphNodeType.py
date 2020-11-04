import enum

class StreamGraphNodeType(enum.Enum):
    """Enum to determine which type of Node this StreamGraphNode is.
    """
    SINGLE_OUTPUT_STREAM = 1
    SPLIT_STREAM = 2
    JOIN_STREAM = 3