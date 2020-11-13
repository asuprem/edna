from __future__ import annotations

from typing import List, Dict
from edna.core.plans.physicalgraph import PhysicalGraphNode
from edna.exception import PhysicalGraphNodeDoesNotExistException

from edna.core.plans.streamgraph import StreamGraphNode

class PhysicalGraph:
    """A PhysicalGraph represents the physical plan for an edna job. Edna operates on
    pipelined records, where no process in the job graph blocks the stream.

    This can be accomplished by running each process as a separate thread, but this would
    reduce the throughput by adding unnecessary thread-to-thread communication. Edna 
    optimized pipelining in the PhysicalGraph by building PhysicalGraphNodes that group
    multiple consecutive 1-to-1 processes. 

    The StreamGraph is split into groups at edna processes that do not conform to the 
    1-to-1 paradigm (such as splits or joins), as well as at processes that flatten or aggregate.
    Each PhysicalGraphNode in the PhysicalGraph contains its own internal StreamGraph representing
    these sub-job groups, and can be run on a separate thread. Edna completes the PhysicalGraph
    with metadata for thread-to-thread communication using the TCP stack to pass
    records through the job graph.

    The `edna.core.plans.physicalgraph.PhysicalGraphBuilder`
    can  be used to convert a flattened StreamGraph to a PhysicalGraph.

    Attributes:
        physical_node_list (List[PhysicalGraphNode]): List of all PhysicalGraphNodes in the
            PhysicalGraph.
        physical_nodes_edges (Dict[int,List[int]]): Source and target PhysicalGraphNode
            for the edges in the PhysicalGraph
        stream_nodes_edges (Dict[int, List[int]]): Source and target nodes of the StreamGraph this
            PhysicalGraph is representing. Currently unused. As the StreamGraph is converted,
            its edges are recorded here for consistency checks.
        physical_node_head (int): The current head node. Modifications to the PhysicalGraph are made
            to this node.
        stream_nodes_to_physical_nodes_map (Dict[int, int]): Records which PhysicalGraphNode a
            StreamGraphNode is stored in, referenced by their respective node ids
        physical_node_ids_to_physical_node_idx_map (Dict[int,int]): Keyed by node id, records the 
            index in the `physical_node_list` that contains the PhysicalGraphNode with the node id.
        physical_node_root_list (Dict[int,int]): List of roots of the PhysicalGraph.
    
    """
    # This will store the list of nodes
    physical_node_list : List[PhysicalGraphNode]
    # Each time we add a connection, the node_map is updated for the current context
    physical_nodes_edges : Dict[int,List[int]]
    stream_nodes_edges: Dict[int, List[int]]    # UNEEDED?
    # Index of node in node_list that is the current head of graph (things will be attached to this...)
    physical_node_head : int
    # this will store the mapping of streeamgraphnodes to physicalgraphnodes. Stream graph node ids are mapped to physical node id
    stream_nodes_to_physical_nodes_map: Dict[int, int]
    # Record a reference to the physical node in node_list given the physical node id
    physical_node_ids_to_physical_node_idx_map: Dict[int,int]
    # List of roots
    physical_node_root_list: Dict[int,int]



    def __init__(self):
        """Initializes an empty PhysicalGraph
        """
        self.physical_node_list = []
        self.physical_nodes_edges = {}
        self.stream_nodes_edges = {}
        self.physical_node_head = None
        self.stream_nodes_to_physical_nodes_map = {}
        self.physical_node_ids_to_physical_node_idx_map = {}
        self.physical_node_root_list = {}


    def addPhysicalGraphNode(self, physical_graph_node: PhysicalGraphNode):
        """Adds a new PhysicalGraphNode. If the node is not empty, its internal 
        StreamGraphNodes are added the the PhysicalGraph as well.

        Args:
            physical_graph_node (PhysicalGraphNode): The PhysicalGraphNode to add.

        Raises:
            RuntimeError: If any StreamGraphNode inside the PhysicalGraphNode already
                exists in the PhysicalGraph.
        """
        for stream_graph_node in physical_graph_node.stream_graph_node_list:
            if self.streamNodeExistsInPhysicalGraphNode(stream_graph_node.node_id):
                raise RuntimeError("Stream graph node already exists in stream nodes map...")

        self.physical_node_list.append(physical_graph_node)
        self.physical_node_head = len(self.physical_node_list) - 1
        for stream_graph_node in physical_graph_node.stream_graph_node_list:
            self.stream_nodes_map[stream_graph_node.node_id] = physical_graph_node.node_id
        self.physical_node_ids_to_physical_node_idx_map[physical_graph_node.node_id] = self.physical_node_head
        self.physical_node_root_list[self.physical_node_head] = 1

    def streamNodeExistsInPhysicalGraphNode(self, stream_graph_node_id: int) -> bool:
        """This checks whether a StreamGraphNode already exists within the PhysicalGraph

        Args:
            stream_graph_node_id (int): The node id of the StreamGraphNode to check.

        Returns:
            bool: If the requested StreamGraphNode exists.
        """
        return stream_graph_node_id in self.stream_nodes_to_physical_nodes_map

    #------ GETTING NODES -----------------------------------------
    def getPhysicalGraphNodeIndexByPhysicalNodeId(self, node_id: int) -> int:
        """Returns the index of a PhysicalGraphNode referenced by node id

        Args:
            node_id (int): The id of the node to retrieve the index.

        Raises:
            PhysicalGraphNodeDoesNotExistException: Raised if the requested node
                does not exist

        Returns:
            int: The index of the PhysicalGraphNode in the `physical_node_list`
        """
        node_idx = self.physical_node_ids_to_physical_node_idx_map.get(node_id, None)
        if node_idx is None:
            raise PhysicalGraphNodeDoesNotExistException(node_id=node_id)
        return node_idx

    def getPhysicalGraphNodeByIndex(self, idx: int) -> PhysicalGraphNode:
        """Returns a PhysicalGraphNode referenced by its index.

        Args:
            idx (int): The index of the node to retrieve.

        Returns:
            PhysicalGraphNode: The requested node
        """
        return self.physical_node_list[idx]

    def getPhysicalGraphNodeByStreamNodeId(self, node_id: int) -> PhysicalGraphNode:
        """Returns a PhysicalGraphNode referenced by its index.

        Args:
            node_id (int): The id of the node to retrieve.

        Returns:
            PhysicalGraphNode: The requested node
        """
        return self.physical_node_list[self.getPhysicalGraphNodeIndexByPhysicalNodeId(self.stream_nodes_to_physical_nodes_map[node_id])]

    def getHeadByPhysicalNodeId(self, node_id: int) -> PhysicalGraph:
        """Changes the head node of the PhysicalGraph to the requested 
        node referenced by id.

        Args:
            node_id (int): The id of the node to set as head.

        Returns:
            PhysicalGraph: An instance of this PhysicalGraph, with a modified head.
        """
        self.physical_node_head = self.getPhysicalGraphNodeIndexByPhysicalNodeId(node_id=node_id)
        return self
    
    def getHeadByStreamNodeId(self, node_id: int) -> PhysicalGraph:
        """Changes the head node of the PhysicalGraph to the requested 
        node referenced by a StreamGraphNode id, where the requested head contains
        the StreamGraphNode.

        Args:
            node_id (int): The node id of the StreamGraphNode

        Returns:
            PhysicalGraph: An instance of this PhysicalGraph, with a modified head.
        """
        self.physical_node_head = self.getPhysicalGraphNodeIndexByPhysicalNodeId(self.stream_nodes_to_physical_nodes_map[node_id])
        return self

    def getPhysicalNodeIdOfHead(self) -> int:
        """Returns the node id of the head PhysicalGraphNode

        Returns:
            int: The node id of the head node
        """
        return self.physical_node_list[self.physical_node_head].node_id

    def isChainable(self) -> bool:
        """Checks if the head PhysicalGraphNode is chainable. A PhysicalGraphNode
        is chainable if new StreamGraphNodes can be added to it. This means
        the node does not yet have an emit node inside it.

        Returns:
            bool: [description]
        """
        return self.physical_node_list[self.physical_node_head].isChainable()


    #------ ADDING NODES -----------------------------------------
    def insertIngestNodeInHead(self, ingest_node: StreamGraphNode):
        """Inserts an ingest StreamGraphNode inside the head PhysicalGraphNode.

        Args:
            ingest_node (StreamGraphNode): The StreamGraphNode to insert.

        Raises:
            RuntimeError: Raised if the StreamGraphNode already exists somewhere in the 
                PhysicalGraph.
        """
        if self.streamNodeExistsInPhysicalGraphNode(ingest_node.node_id):
            raise RuntimeError("Ingest Stream Node already exists...?")    # TODO We need out completed node list...in Builder
        self.physical_node_list[self.physical_node_head].addIngestNode(ingest_node)
        # This maps a stream node id to the id of the phyisical node that contains it
        self.stream_nodes_to_physical_nodes_map[ingest_node.node_id] = self.physical_node_list[self.physical_node_head].node_id

    def insertEmitNodeInHead(self, emit_node: StreamGraphNode):
        """Inserts an emit StreamGraphNode inside the head PhysicalGraphNode.

        Args:
            emit_node (StreamGraphNode): The StreamGraphNode to insert.

        Raises:
            RuntimeError: Raised if the StreamGraphNode already exists somewhere in the 
                PhysicalGraph.
        """
        if self.streamNodeExistsInPhysicalGraphNode(emit_node.node_id):
            raise RuntimeError("Emit Stream Node already exists...?")    # TODO We need out completed node list...in Builder
        self.physical_node_list[self.physical_node_head].addEmitNode(emit_node)
        # This maps a stream node id to the id of the phyisical node that contains it
        self.stream_nodes_to_physical_nodes_map[emit_node.node_id] = self.physical_node_list[self.physical_node_head].node_id
        # We need to add placeholders for the edge, unless this is a true Emit...so how do we check?


    def insertProcessNodeInHead(self, process_node: StreamGraphNode):
        """Inserts a process StreamGraphNode inside the head PhysicalGraphNode.

        Args:
            process_node (StreamGraphNode): The StreamGraphNode to insert.

        Raises:
            RuntimeError: Raised if the StreamGraphNode already exists somewhere in the 
                PhysicalGraph.
        """
        if self.streamNodeExistsInPhysicalGraphNode(process_node.node_id):
            raise RuntimeError("Emit Stream Node already exists...?")    # TODO We need out completed node list...in Builder
        self.physical_node_list[self.physical_node_head].addProcessNode(process_node)
        # This maps a stream node id to the id of the phyisical node that contains it
        self.stream_nodes_to_physical_nodes_map[process_node.node_id] = self.physical_node_list[self.physical_node_head].node_id
        # We need to add placeholders for the edge, unless this is a true Emit...so how do we check?



    #---------- ADDING EDGES ----------------------------------------
    # 1-1, join node
    def addEdge(self, source_physical_node_id: int, target_physical_node_id: int):
        """Add an edge between a source PhysicalGraphNode and a target PhysicalGraphNode,
        each referenced by their node ids

        Args:
            source_physical_node_id (int): The id of the source PhysicalGraphNode for the edge
            target_physical_node_id (int): The id of the target PhysicalGraphNode for the edge
        """
        # TODO we will add placeholder edge in addEmit, addSplit, etc...
        self.physical_nodes_edges[source_physical_node_id] = [target_physical_node_id]
        # remove the target from root list
        if self.getPhysicalGraphNodeIndexByPhysicalNodeId(target_physical_node_id) in self.physical_node_root_list:
            self.physical_node_root_list.pop(self.getPhysicalGraphNodeIndexByPhysicalNodeId(target_physical_node_id))

    def addPlaceholderEdge(self, source_physical_node_id: int, num_edges: int = 1):
        """Adds placeholder edges to a PhysicalGraphNode

        Args:
            source_physical_node_id (int): The id of the source PhysicalGraphNode for the placeholder edges
            num_edges (int, optional): The number of placeholder edges to add. Defaults to 1.
        """
        # TODO for split...? Also, need to make sure we verify graph at end so there are no remaining placeholder edges.
        self.physical_nodes_edges[source_physical_node_id] = [None]*num_edges

    def replacePlaceholderEdge(self, source_physical_node_id: int, target_physical_node_id: int, placeholder_idx: int):
        """Replace a palceholder edge with an actual edge

        Args:
            source_physical_node_id (int): The id of the source PhysicalGraphNode for the placeholder edge
            target_physical_node_id (int): The id of the target PhysicalGraphNode for the placeholder edge
            placeholder_idx (int): The placeholder index to replace
        """
        self.physical_nodes_edges[source_physical_node_id][placeholder_idx] = target_physical_node_id
        if self.getPhysicalGraphNodeIndexByPhysicalNodeId(target_physical_node_id) in self.physical_node_root_list:
            self.physical_node_root_list.pop(self.getPhysicalGraphNodeIndexByPhysicalNodeId(target_physical_node_id))

    def getEdgesForPhysicalNodeId(self, physical_node_id: int) -> List[int]:
        """Returns the edges for a PhysicalGraphNode, referenced by id.

        Args:
            physical_node_id (int): The node id of the PhysicalGraphNode

        Returns:
            List[int]: Returns a list of node ids that are targets for the provided source node.
        """
        return self.physical_nodes_edges.get(physical_node_id,[])

    def getEdgesForPhysicalNodeIdx(self, physical_node_idx: int) -> List[int]:
        """Returns the edges for a PhysicalGraphNode, referenced by index.

        Args:
            physical_node_idx (int): The node index of the PhysicalGraphNode

        Returns:
            List[int]: Returns a list of node ids that are targets for the provided source node.
        """
        return self.getEdgesForPhysicalNodeId(self.physical_node_list[physical_node_idx].node_id)
        

    

    








    """Types of physicalgraphnodes:
        - ingest-primitive - contains just a source
            for item in ingest: 
                o_buffer(message)
        - process-primitive - contains just a process
            for item in i_buffer:
                o_buffer(process())
        - emit-primitive - contains just an emit
            for item in i_buffer:
                emit()
        - ingest-process-primitive - contains a source and process
            for item in ingest:
                o_buffer(process)
        - process-process-primitive - maybe same as process-primitive.
            for item in i_buffer:
                o_buffer(process())
        - process-emit-primitive - contains process and emit
            for item in i_buffer:
                emit(process())
        - ingest-emit-primitive - contains ingest and emit
            for item in ingest

    the graph will also store a list of streamgraphnodes, and which 

    """







