import enum

class StreamGraphNodeType(enum.Enum):
    """Enum to determine which type of Node this StreamGraphNode is.

    A SINGLE_OUTPUT_STREAM is a node with a single input and single output stream.

    A SPLIT_STREAM is a node with a single input and multiple output streams.

    A JOIN_STREAM is a node with multiple input and single output streams.

    Nodes for multiple input multiple output streams can be built with a JOIN_STREAM node
    followed by a SPLIT_STREAM node.
    """
    SINGLE_OUTPUT_STREAM = 1
    SPLIT_STREAM = 2
    JOIN_STREAM = 3