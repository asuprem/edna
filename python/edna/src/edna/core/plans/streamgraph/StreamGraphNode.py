from __future__ import annotations
from typing import Callable

from edna.types.enums import StreamGraphNodeType
from edna.types.builtin import GraphNode

class StreamGraphNode(GraphNode):
    """A `StreamGraphNode` is the base class for nodes in a `edna.core.plans.streamgraph.StreamGraph`.
    StreamGraphNodes wrap individual edna primitives and represent the nodes of the job graph
    of an edna job. They are connected in a DAG in a `StreamGraph`. 

    Attributes:
        stream_graph_node_type (StreamGraphNodeType): This categorizes a `StreamGraphNode` on its number of 
            outputs and inputs: single-output, multi-output, and multi-inputs.
    """
    stream_graph_node_type : StreamGraphNodeType

    