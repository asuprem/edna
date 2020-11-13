from __future__ import annotations
from edna.core.plans.streamgraph import SingleOutputStreamGraphNode
from edna.exception import StreamGraphNodeDoesNotExistException
from typing import Dict, List

class StreamGraph:
    """StreamGraph represents the logical plan for an Edna Job. It records SingleOutputStreamGraphNodes 
    and edges between these nodes. Each node is either a source node that ingests a stream 
    into the StreamGraph, a transformation that modifies the stream, or a sink that emits
    a stream.

    Attributes:
        node_list (List[SingleOutputStreamGraphNode]): This is the list of nodes in the StreamGraph. Each element 
            is a SingleOutputStreamGraphNode encapsulating the transformation callable.
        node_map (Dict[int, List[int]]): This is the representation of the StreamGraph DAG. Each entry 
            in the map is the index of the source node in `node_list`. The values are the list
            of indices of target nodes the source node connects to.
        leaf_list (Dict[int]): A list (technically a map for O(1) access) of node indices that point to nodes
            that are currently leaves in the StreamGraph.
        root_list (Dict[int]): A list of node indices that point to nodes that are currently roots 
            in the StreamGraph.
        empty_graph (bool): Set to `false` when initialized and updated to `true` when a node is added.
        node_head (int): Index of the last modified node in the graph. 
        node_id_to_node_idx_map (Dict[int,int]): A map to retrieve the index of a node in the `node_list`
            given the node's `node_id`
    """
    # This will store the list of nodes
    node_list : List[SingleOutputStreamGraphNode]
    # Each time we add a connection, the node_map is updated for the current context through Datastream
    node_map : Dict[int,List[int]]
    # This is the list of current leaves in the graph
    leaf_list : Dict[int, int]
    # This is the list of roots in the graph
    root_list : List[int]
    empty_graph : bool = True
    # Index of node in node_list that is the current head of graph (things will be attached to this...)
    node_head : int = None
    node_id_to_node_idx_map: Dict[int,int]
    
    def __init__(self):
        """Initialize the StreamGraph with empty `node_list`, `node_map`, and `leaf_list`.
        """
        self.node_list = [] # Stores nodes
        self.node_map = {}  # node list idx -> node list idx
        self.leaf_list = {} # node idx in node_list that are leaf
        self.root_list = [] # node idx in node_list that are roots
        self.node_id_to_node_idx_map = {}   # node id to node idx in node_list

    def addNode(self, node: SingleOutputStreamGraphNode):
        """Add a new node to the StreamGraph and update the head to reference the new node. 
        Also add the node to the list of leafs in the StreamGraph. Updates the 
        `node_id_to_node_idx_map`, and also updates `root_list` if the node is an ingest.

        Args:
            node (SingleOutputStreamGraphNode): A SingleOutputStreamGraphNode instance.

        Raises:
            ValueError: Raised if the StreamGraph is empty and the node to be added is not an ingest node.
        """
        # TODO make sure the first entry is a root...maybe datastream will manage this?
        if self.empty_graph:
            if not node.isIngest():
                raise ValueError("First node inserted into StreamGraph must be an ingest node")
        
        
        self.node_list.append(node)
        self.node_head = len(self.node_list) - 1
        
        self.empty_graph = False

        if node.isIngest():
            self.root_list.append(self.node_head)
        
        self.leaf_list[self.node_head] = 1
        self.node_id_to_node_idx_map[node.node_id] = self.node_head

    def addNodeToHead(self, node: StreamGraph):
        """Add a node to the StreamGraph and create an edge to the new node from the current head.

        Args:
            node (StreamGraph): The node to add to the StreamGraph DAG
        """
        previous_head = self.node_head
        self.addNode(node)
        self.addEdge(previous_head, self.getHeadNodeIndex())

    def addEdge(self, node1_idx : int, node2_idx: int):
        """Add an edge to the StreamGraph between the nodes referenced by the Node Index

        Args:
            node1_idx (int): Index of the source node in `node_list`
            node2_idx (int): Index of the target node in `node_list`
        """
        # TODO make sure node1 exists in the self.node_map
        self.checkNodeIndexInGraph(node1_idx)
        # Make sure node2 exists in node_list
        if not self.verifyNodeExistsByIndex(node2_idx):
            raise ValueError("Node must be added to StreamGraph before adding edge.")
        self._addEdge(node1_idx, node2_idx)

    def addPlaceholderEdge(self, node1_idx : int):
        """Add an edge between provided node and a placeholder node

        Args:
            node1_idx (int): Index of the source node in `node_list``
        """
        # TODO make sure node1 exists in the self.node_list
        self.checkNodeIndexInGraph(node1_idx)
        self._addPlaceholderEdge(node1_idx)

    def updatePlaceholderEdge(self, node1_idx : int, node2_idx: int, edge_idx: int):
        """Update an existing placeholder edge with a correct edge

        Args:
            node1_idx (int): Index of the source node in `node_list``
        """
        # TODO make sure node1 exists in the self.node_list
        self.checkNodeIndexInGraph(node1_idx)
        if not self.verifyNodeExistsByIndex(node2_idx):
            raise ValueError("Node must be added to StreamGraph before adding edge.")
        self._updatePlaceholderEdge(node1_idx, node2_idx, edge_idx)

    def _addEdge(self, node1_idx: int, node2_idx: int):
        """Internal function to add the edge in StreamGraph. If the source node was a leaf, it is removed from the `leaf_list`.

        Args:
            node1_idx (int): The source node index.
            node2_idx (int): The target node index.

        Raises:
            ValueError: Raised if edge already exists.
        """
        if node2_idx in self.node_map[node1_idx]:
            raise ValueError("Node {target_node_name} already exists as a connecton to Node {source_node_name}"
                .format(target_node_name=self.node_list[node2_idx].name, 
                        source_node_name=self.node_list[node1_idx].name)
                        )
        if self.node_list[node1_idx].isEmit():
            raise RuntimeError("Cannot add a process node to an emit node. Add a new stream root first.")
        self.node_map[node1_idx].append(node2_idx)
        self.removeIfLeaf(node1_idx)

    def _addPlaceholderEdge(self, node_idx: int):
        """Internal function to add a placeholder edge in StreamGraph.

        Args:
            node1_idx (int): The source node index.

        Raises:
            ValueError: Raised if edge already exists.
        """
        if self.node_list[node_idx].isEmit():
            raise RuntimeError("Cannot add a process node to an emit node. Add a new stream root first.")
        self.node_map[node_idx].append(None)

    def _updatePlaceholderEdge(self, node1_idx: int, node2_idx : int, edge_idx : int):
        """Internal function to update a placeholder edge in StreamGraph.

        Args:
            node1_idx (int): The source node index.

        Raises:
            ValueError: Raised if edge already exists.
        """
        if node2_idx in self.node_map[node1_idx]:
            raise ValueError("Node {target_node_name} already exists as a connecton to Node {source_node_name}"
                .format(target_node_name=self.node_list[node2_idx].name, 
                        source_node_name=self.node_list[node1_idx].name)
                        )
        if self.node_list[node1_idx].isEmit():
            raise RuntimeError("Cannot add a process node to an emit node. Add a new stream root first.")
        self.node_map[node1_idx][edge_idx] = node2_idx
        self.removeIfLeaf(node1_idx)

    # Get node by the head
    def getHeadNodeIndex(self):
        """Gets the index of the current head of the StreamGraph

        Returns:
            (int): The index of the current head of the StreamGraph
        """
        return self.node_head

    def getNodeByIndex(self, node_idx):
        """Get a node from `node_list` at the given `node_idx`

        Args:
            node_idx (int): The index of the node to retrieve from `node_list`

        Returns:
            SingleOutputStreamGraphNode: Returns the node at `node_idx` in `node_list`
        """
        return self.node_list[node_idx]

    def getNodeIndexByNodeName(self, name: str):
        """Get a node index from `node_list` given the name of the node and sets the current head to this node.

        Args:
            name (str): The name of the node to retrieve from `node_list`

        Raises:
            SingleOutputStreamGraphNodeDoesNotExistException: If the requested node does not exist in `node_list`

        Returns:
            int: Returns the node index with the name matching the requested name.
        """
        self.setNodeHeadByName(node_name=name)
        return self.getHeadNodeIndex()

    def getNodeIndexByNodeId(self, node_id: int):
        """Get a node index from `node_list` given the id of the node and sets the current head to this node.

        Args:
            node_id (int): The id of the node to retrieve from `node_list`

        Raises:
            StreamGraphNodeDoesNotExistException: If the requested node does not exist in `node_list`

        Returns:
            int: Returns the node index with the id matching the requested id.
        """
        self.setNodeHeadById(node_id=node_id)
        return self.getHeadNodeIndex()
    
    def setNodeHeadByName(self, node_name: str):
        node_idx = None
        for idx, node in enumerate(self.node_list):
            if node.name == node_name:
                node_idx = idx
                break
        if node_idx is None:
            raise StreamGraphNodeDoesNotExistException(name=node_name)
        self.node_head = node_idx

    def setNodeHeadById(self, node_id: int):
        node_idx = self.node_id_to_node_idx_map.get(node_id,None)
        """
        for idx, node in enumerate(self.node_list):
            if node.node_id == node_id:
                node_idx = idx
                break
        """
        if node_idx is None:
            raise StreamGraphNodeDoesNotExistException(node_id==node_id)
        self.node_head = node_idx

    def checkNodeIndexInGraph(self, node_idx: int):
        """Check if the given index exists in the `node_list` and in the `node_map` Map.

        Args:
            node_idx (int): The index of the node to check in `node_list`
        """
        if not self.verifyNodeExistsByIndex(node_idx):
            raise ValueError("Node must be added to StreamGraph before adding edge.")
        if node_idx not in self.node_map:
            self.addVertex(node_idx)
        
    def verifyNodeExistsByIndex(self, node_idx: int):
        """Check if the given  node_idx is actually inside the `node_list`

        Args:
            node_idx (int): The index of the node to check.

        Raises:
            ValueError: Raised if the size of `node_list` is smaller than the `node_idx`
        """
        return len(self.node_list)-1 >= node_idx

    def verifyNodeExistsById(self, node_id: int) -> bool:
        """Verifies if a node with the provided `node_id` exists in the StreamGraph.

        Args:
            node_id (int): The node id to check.

        Returns:
            (bool): Whether the desired node exists
        """
        return node_id in self.node_id_to_node_idx_map

    def verifyNodeExistsByName(self, node_name: str) -> bool:
        """Verifies if a node with the provided `name` exists in the StreamGraph.

        Args:
            node_name (str): The node name to check

        Returns:
            bool: Whether the desired node exists
        """
        node_idx = None
        for idx, node in enumerate(self.node_list):
            if node.name == node_name:
                return True
        return False

    def addVertex(self, node_idx: int):
        """Adds a `node_idx` to the `node_map` with an empty edge list.

        Args:
            node_idx (int): The index of the node to add to the `node_map`
        """
        self.node_map[node_idx] = []


    def isLeaf(self, node_idx: int) -> bool:
        """Checks if the given index is of a leaf node.

        Args:
            node_idx (int): The node index to check

        Returns:
            (bool): Returns if `node_idx` refers to a leaf node.
        """
        return node_idx in self.leaf_list

    def removeIfLeaf(self, node_idx: int):
        """Remove a node from `leaf_list` if it is a leaf.

        Args:
            node_idx (int): The node index to remove.
        """
        if self.isLeaf(node_idx=node_idx):
            self.deleteLeaf(node_idx=node_idx)

    def deleteLeaf(self, node_idx: int):
        """Remove a leaf node from `leaf_list`

        Args:
            node_idx (int): The node index to remove.
        """
        self.leaf_list.pop(node_idx)

    def verifyGraph(self) -> bool:
        """Verify the graph, ensuring all leaf nodes are Emit Nodes.

        Returns:
            bool: Returns True if the StreamGraph is a valid stream graph.
        """
        leaf_verify = True
        for node_idx in self.leaf_list:
            if not self.node_list[node_idx].isEmit():
                leaf_verify = False

        return leaf_verify


    # Node operations
    def setNodeNameById(self, node_id : int, node_name: str):
        """Sets the name of a node, referenced by the node id.

        Args:
            node_id (int): The node id to target
            node_name (str): The new name for this node
        """
        self.setNodeNameByIndex(node_index=self.getNodeIndexByNodeId(node_id=node_id), node_name=node_name)

    def setNodeNameOfHead(self, node_name: str):
        """Set the name of the head node.

        Args:
            node_name (str): The new name for the head node
        """
        self.setNodeNameByIndex(self.getHeadNodeIndex(), node_name=node_name)
    
    def setNodeNameByIndex(self, node_index : int, node_name: str):
        """Sets the name of a node, referenced by the node index.

        Args:
            node_index (int): The node index to target
            node_name (str): The new name for this node
        """
        self.node_list[node_index].setName(node_name)

    def getNodeNameById(self, node_id: int) -> str:
        """Get the name of a node referenced by the node id

        Args:
            node_id (int): The id of the target node.

        Returns:
            str: The name of the node
        """
        return self.getNodeNameByIndex(self.getNodeIndexByNodeId(node_id=node_id))

    def getNodeNameOfHead(self) -> str:
        """Get the name of the head node

        Returns:
            str: [description]
        """
        return self.getNodeNameByIndex(self.getHeadNodeIndex())

    def getNodeNameByIndex(self, node_index: int) -> str:
        """Get the name of a node referenced by the node indedx

        Args:
            node_index (int): The index of the target node.

        Returns:
            str: The name of the node
        """
        return self.node_list[node_index].getName()


    def getHeadNode(self) -> SingleOutputStreamGraphNode:
        """Get the current head node.

        Returns:
            SingleOutputStreamGraphNode: The desired node
        """
        return self.node_list[self.node_head]
    
    def getNodeByIndex(self, node_index : int) -> SingleOutputStreamGraphNode:
        """Get a node referenced by the node index

        Args:
            node_index (int): The index of the node to retrieve

        Returns:
            SingleOutputStreamGraphNode: The desired node
        """
        return self.node_list[node_index]

    def getNodeById(self, node_id : int) -> SingleOutputStreamGraphNode:
        """Get a node referenced by the node id

        Args:
            node_id (int): The id of the node to retrieve

        Returns:
            SingleOutputStreamGraphNode: The desired node
        """
        return self.getNodeByIndex(self.getNodeIndexByNodeId(node_id=node_id))

    def getNodeByName(self, node_name: str) -> SingleOutputStreamGraphNode:
        """Get a node referenced by the node name

        Args:
            node_name (str): The name of the node to retrieve

        Returns:
            SingleOutputStreamGraphNode: The desired node
        """
        return self.getNodeByIndex(self.getNodeIndexByNodeName(node_name))

    
    def getEdgesForNodeId(self, node_id: int) -> List[int]:
        """Gets the edges for a node referencced by the node id

        Args:
            node_id (int): The id of the node to get the edges for.

        Returns:
            List[int]: The list of target nodes of this source node.
        """
        return self.getEdgesForNodeIdx(self.getNodeIndexByNodeId(node_id))

    def getEdgesForNodeIdx(self, node_idx: int) -> List[int]:
        """Gets the edges for a node referencced by the node index

        Args:
            node_idx (int): The index of the node to get the edges for.

        Returns:
            List[int]: The list of target nodes of this source node.
        """
        return self.node_map.get(node_idx,[])