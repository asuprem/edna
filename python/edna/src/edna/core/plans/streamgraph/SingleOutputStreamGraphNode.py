from edna.types.enums import StreamGraphNodeType
from edna.core.plans.streamgraph import StreamGraphNode

from edna.types.enums import SingleOutputStreamGraphNodeProcessType
from edna.types.enums import SingleOutputStreamGraphNodeType
from typing import Callable

class SingleOutputStreamGraphNode(StreamGraphNode):
    node_type: SingleOutputStreamGraphNodeType  # This is ingest-process-emit
    process_node_type: SingleOutputStreamGraphNodeProcessType # This is map, filter, etc
    node_callable: Callable

    ingest_node_type: bool = False
    process_node_type: bool = False
    emit_node_type: bool = False

    def __init__(self, node_type: SingleOutputStreamGraphNodeType, node_id: int, name: str = None, node_callable: Callable = None, process_node_type: SingleOutputStreamGraphNodeProcessType = None):
        super().__init__(node_id=node_id, name=name)
        self.node_type = node_type
        self.process_node_type = process_node_type
        self.node_callable = node_callable    
        self.stream_graph_node_type = StreamGraphNodeType.SINGLE_OUTPUT_STREAM
        self.setNodeType()


    def setNodeType(self):
        if self.node_type == SingleOutputStreamGraphNodeType.INGEST:
            self.ingest_node_type = True
        elif self.node_type == SingleOutputStreamGraphNodeType.PROCESS:
            self.process_node_type = True
        elif self.node_type == SingleOutputStreamGraphNodeType.EMIT:
            self.emit_node_type = True
        else:
            raise RuntimeError("Incorrect node_type for StreamGraphNode.")


    def isIngest(self):
        return self.ingest_node_type

    def isProcess(self):
        return self.process_node_type

    def  isEmit(self):
        return self.emit_node_type

    