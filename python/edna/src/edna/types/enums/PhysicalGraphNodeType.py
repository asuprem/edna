import enum

class PhysicalGraphNodeType(enum.Enum):
    """Enum to determine which type of Node this PhysicalGraphNode is.

    A SINGLE_OUTPUT_NODE has a single input and a single output stream.

    A SPLIT_OUTPUT_NODE has a single input and multiple output streams.

    A JOIN_INPUT_NODE has multiple input and single output streams.

    A JOIN_INPUT_SPLIT_OUTPUT_NODE has multiple input and multiple output streams.
    """
    SINGLE_OUTPUT_NODE = 1
    SPLIT_OUTPUT_NODE = 2
    JOIN_INPUT_NODE = 3
    JOIN_INPUT_SPLIT_OUTPUT_NODE = 4