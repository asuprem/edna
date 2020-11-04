import enum

class PhysicalGraphNodeType(enum.Enum):
    """Enum to determine which type of Node this PhysicalGraphNode is.
    """
    SINGLE_OUTPUT_NODE = 1
    SPLIT_OUTPUT_NODE = 2