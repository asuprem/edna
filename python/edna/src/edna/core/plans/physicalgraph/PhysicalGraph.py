from __future__ import annotations

from typing import List, Dict
from edna.core.plans.physicalgraph import PhysicalGraphNode
from edna.exception import PhysicalGraphNodeDoesNotExistException


class PhysicalGraph:
    

    # This will store the list of nodes
    node_list : List[PhysicalGraphNode]
    # Each time we add a connection, the node_map is updated for the current context
    node_map : Dict[int,List[int]]
    # Index of node in node_list that is the current head of graph (things will be attached to this...)
    node_head : int = None
    # this will store the mapping of streeamgraphnodes to physicalgraphnodes. Stream graph node ids are mapped to physical node id
    stream_nodes_map: Dict[int, int]


    def __init__(self):
        self.node_list = []
        self.node_map = {}
        self.stream_nodes_map = {}

    def addPhysicalGraphNode(self, node: PhysicalGraphNode):
        self.node_list.append(node)
        self.node_head = len(self.node_list) - 1

        for stream_graph_node in node.stream_graph_node_list:
            if stream_graph_node.node_id in self.stream_nodes_map:
                raise RuntimeError("Stream graph node already exists in stream nodes map...")
            
            self.stream_nodes_map[stream_graph_node.node_id] = node.node_id
            



    def getPhysicalGraphNodeIndexById(self, node_id: int):
        node_idx = None
        for idx, node in enumerate(self.node_list):
            if node.node_id == node_id:
                node_idx = idx
                break
        if node_idx is None:
            raise PhysicalGraphNodeDoesNotExistException(node_id=node_id)
        return node_idx

    
















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