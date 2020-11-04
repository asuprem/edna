from __future__ import annotations

from typing import List, Dict

from edna.core.plans.streamgraph import StreamGraphNode
from edna.types.enums import PhysicalGraphNodeType
from edna.types.builtin import GraphNode
from edna.utils.NameUtils import NameUtils

class PhysicalGraphNode(GraphNode):
    physical_graph_node_type : PhysicalGraphNodeType
    stream_graph_node_list: List[StreamGraphNode]
    empty_graph : bool = True
    node_head : int = None

    def __init__(self, node_id: int, name: str = None):
        super().__init__(name=name, node_id=node_id)
        self.stream_graph_node_list = []
        self.physical_graph_node_type = PhysicalGraphNodeType.SINGLE_OUTPUT_NODE

    def addNode(self, stream_graph_node: StreamGraphNode):
        self.stream_graph_node_list.append(stream_graph_node)
        self.node_head = len(self.stream_graph_node_list) - 1
    
        
        
    


    
    