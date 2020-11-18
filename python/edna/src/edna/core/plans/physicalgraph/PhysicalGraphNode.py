from __future__ import annotations

from typing import ChainMap, List, Dict

from edna.core.plans.streamgraph import StreamGraphNode
from edna.types.enums import PhysicalGraphNodeType
from edna.types.builtin import GraphNode
from edna.core.plans.streamgraph import StreamGraph

class PhysicalGraphNode(GraphNode):
    """A PhysicalGraphNode is a non-branching DAG encapsulating 1-to-1 edna processes. Each PhysicalGraphNode must be composed 
    of the <ingest-process-emit> primitives, but all need not exist.
    
    Ingest can be a StreamGraphNode encapsulating an edna ingest, or a buffer-ingest. A buffer-ingest is instrinsically tied to the 
    PhysicalGraph, since it must specify the parent PhysicalGraphNode that will send records to this buffer ingest. Ingest can also be
    a join.

    Emit can be a StreamGraphNode encapsulating an edna emit or a buffer-emit. Buffer-emits do not need to store where they send data.
    Emit can also be a Split. In this case, PhysicalGraphNode can have multiple emits ports.

    Process is a StreamGraphNode wrapping an edna process. It can be a map or filter. Note that a flatten or aggregate falls under either emit
    or ingest, respectively.

    Attributes:
        physical_graph_node_type (PhysicalGraphNodeType): The node type for this PhysicalGraphNode
        internal_stream_graph (StreamGraph): The internal StreamGraph for this PhysicalGraphNode
        empty_graph (bool): Whether the node is empty.
        chainable (bool): Whether the node is chainable.
    """
    physical_graph_node_type : PhysicalGraphNodeType    # SINGLE_OUTPUT, SPLIT_OUTPUT, etc...
    internal_stream_graph : StreamGraph
    empty_graph : bool
    chainable : bool

    def __init__(self, node_id: int, name: str = None):
        """Initializes an empty PhhysicalGraphNode

        Args:
            node_id (int): The node id for this PhysicalGraphNode
            name (str, optional): The name for this PhysicalGraphNode. Defaults to None.
        """
        super().__init__(name=name, node_id=node_id)
        self.stream_graph_node_list = []
        self.internal_stream_graph = StreamGraph()
        self.physical_graph_node_type = PhysicalGraphNodeType.SINGLE_OUTPUT_NODE
        self.empty_graph = True
        self.chainable = True

    # Add an ingest node to the stream graph
    def addIngestNode(self, stream_graph_node: StreamGraphNode):
        """Adds the provided ingest node. The PhysicalGraphNode should be chainable.
        Raises a RuntimeError if the node is not chainable.

        Args:
            stream_graph_node (StreamGraphNode): The StreamGraphNode to add
        """
        self._addable()
        self.internal_stream_graph.addNode(stream_graph_node)

    def addProcessNode(self, stream_graph_node: StreamGraphNode):
        """Adds the provided process node. The PhysicalGraphNode should be chainable.
        Raises a RuntimeError if the node is not chainable.

        Args:
            stream_graph_node (StreamGraphNode): The StreamGraphNode to add
        """
        self._addable()
        self.internal_stream_graph.addNodeToHead(stream_graph_node)

    def addEmitNode(self, stream_graph_node: StreamGraphNode):
        """Adds the provided ingest node. The PhysicalGraphNode should be chainable.
        Raises a RuntimeError if the node is not chainable. Sets `chainable` to False.

        Args:
            stream_graph_node (StreamGraphNode): The StreamGraphNode to add
        """
        self._addable()
        self.internal_stream_graph.addNodeToHead(stream_graph_node)
        self.chainable = False
        
    def _addable(self):
        """Checks if a StreamGraphNode can be added to this PhysicalGraphNode

        Raises:
            RuntimeError: Raised if PhysicalGraphNode is not chainable.
        """
        if not self.isChainable():
            raise RuntimeError("Physical Graph Node is not chainable.")
        
    def isChainable(self) -> bool:
        """Returns if this node is chainable.

        Returns:
            bool: Whether the node is chainable.
        """
        return self.chainable
        
    


    
    