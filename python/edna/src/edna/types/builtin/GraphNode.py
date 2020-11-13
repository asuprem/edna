from __future__ import annotations

from edna.utils.NameUtils import NameUtils


class GraphNode:
    """The base class for a GraphNode for edna's StreamGraphs and PhysicalGraphs.
    The GraphNode records the node id for the node, and a node name, if provided.
    If no name is provided, a random string is generated.

    Attributes:
        name (str): The name for this GraphNode
        node_id (int): The id for this GraphNode
    """
    name: str
    node_id: int
    
    def __init__(self, node_id: int, name: str = None):
        """Initializes this GraphNode with the provided parameters.

        Args:
            node_id (int): The id for this GraphNode
            name (str, optional): The name for this GraphNode. Defaults to None.
        """
        self.node_id = node_id
        if name is None:
            self.setName(NameUtils.createNameSuffix(suffix_length=10))
        else:
            self.setName(name)

    def setName(self, name: str):
        """Sets the provided name for the GraphNode

        Args:
            name (str): The name for this GraphNode.
        """
        self.name = name

    def getName(self) -> str:
        """Gets the name for the GraphNode

        Returns:
            (str): The name of this GraphNode
        """
        return self.name

    def getNodeId(self) -> int:
        """Gets the id for this node

        Returns:
            int: The id of this GraphNode
        """
        return self.node_id