from __future__ import annotations
from typing import Callable

from edna.types.enums import StreamGraphNodeType
from edna.types.builtin import GraphNode

class StreamGraphNode(GraphNode):
    stream_graph_node_type : StreamGraphNodeType

    