from edna.core.primitives import EdnaPrimitive
from edna.types.enums import StreamGraphNodeType
from edna.core.plans.streamgraph import StreamGraphNode

from edna.types.enums import SingleOutputStreamGraphNodeProcessType
from edna.types.enums import SingleOutputStreamGraphNodeType
from typing import Callable

class SingleOutputStreamGraphNode(StreamGraphNode):
    """`SingleOutputStreamGraphNode` represents a logical edna process with a single output. This type
    of `StreamGraphNode` wraps around edna ingest, emit, and process primitives; specifically, edna 
    processes that fall under map, filter, flatten, and aggregate paradigms (see `SingleOutputStreamGraphNodeProcessType`).

    A node stores the callable it wraps, plus labels on whether it is an ingest, process, or emit through
    the `node_type` attribute, and what type of process it is with the `process_node_type` attribute.

    Attributes:
        node_type (SingleOutputStreamGraphNodeType): Stores whether the node is ingest, process, or emit.
        process_node_type (SingleOutputStreamGraphNodeProcessType): If node is process, stores whether it is
            map, flatten, aggregate, or filter
        node_callable (EdnaPrimitive): An edna primitive instance
    
    Raises:
        RuntimeError: Raised when a callable that is not an ingest, process, or emit is passed.

    
    """
    node_type: SingleOutputStreamGraphNodeType  # This is ingest-process-emit
    process_node_type: SingleOutputStreamGraphNodeProcessType # This is map, filter, etc
    node_callable: EdnaPrimitive  # TODO Fix this so that we can add BaseEmit and BaseIngest here...

    def __init__(self, node_type: SingleOutputStreamGraphNodeType, 
            node_id: int, 
            name: str = None, 
            node_callable: EdnaPrimitive = None, 
            process_node_type: SingleOutputStreamGraphNodeProcessType = None):
        """Initializes a SingleOutputStreamGraphNode with the provided callable Primitive, node id, name, and node type.

        Args:
            node_type (SingleOutputStreamGraphNodeType): A `SingleOutputStreamGraphNodeType` corresponding
                to the node callable.
            node_id (int): A node id. This should be unique. `StreamingContext.getNewStreamingNodeId()` provides a 
                node id unique to the current context.
            name (str, optional): An optional name for this node. If no name is provided, a random name will be created
                using `edna.utils.NameUtils`. Defaults to None.
            node_callable (EdnaPrimitive, optional): An edna Primitive for this node. Defaults to None.
            process_node_type (SingleOutputStreamGraphNodeProcessType, optional): The process type if `node_callable`
                is a process. Defaults to None.
        """
        super().__init__(node_id=node_id, name=name)
        self.node_type = node_type
        self.process_node_type = process_node_type
        self.node_callable = node_callable    
        self.stream_graph_node_type = StreamGraphNodeType.SINGLE_OUTPUT_STREAM

    def isIngest(self) -> bool:
        """Returns if this SingleOutputStreamGraphNode wraps an ingest primitive

        Returns:
            (bool): Whether this is an ingest node
        """
        return self.node_type == SingleOutputStreamGraphNodeType.INGEST

    def isProcess(self) -> bool:
        """Returns if this SingleOutputStreamGraphNode wraps a process primitive

        Returns:
            (bool): Whether this is a process node
        """
        return self.node_type == SingleOutputStreamGraphNodeType.PROCESS

    def  isEmit(self) -> bool:
        """Returns if this SingleOutputStreamGraphNode wraps an emit primitive

        Returns:
            (bool): Whether this is an emit node
        """
        return self.node_type == SingleOutputStreamGraphNodeType.EMIT

    