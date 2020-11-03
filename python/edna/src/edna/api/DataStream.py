from __future__ import annotations
from typing import List

from edna.core.plans.streamgraph import StreamGraph
from edna.core.execution.context import StreamingContext

from edna.ingest.streaming import BaseStreamingIngest
from edna.emit import BaseEmit

from edna.core.plans.streamgraph import SingleOutputStreamGraphNode
from edna.types.enums import SingleOutputStreamGraphNodeType
from edna.types.enums import SingleOutputStreamGraphNodeProcessType
from edna.process.map import Map
from edna.process.filter import Filter

class DataStream:
    stream_graph: StreamGraph
    graph_heads: List[int]
    streaming_context: StreamingContext
    stream_id : int = 0

    primary_head_idx: int = 0


    def __init__(self, ingest: BaseStreamingIngest, streaming_context: StreamingContext, stream_id: int, ingest_name: str = None):
        # Build a node with a node-id and node-name
        self.stream_graph = StreamGraph()
        self.graph_heads = []
        self.streaming_context = streaming_context
        self.stream_id = stream_id
        ingest_node = SingleOutputStreamGraphNode(node_type=SingleOutputStreamGraphNodeType.INGEST, 
                        node_id=self.streaming_context.getTransformationId(), name=ingest_name,node_callable=ingest)
        self.addIngestNode(ingest_node)

    def getStreamId(self):
        return self.stream_id
    
    def addIngestNode(self, node: SingleOutputStreamGraphNode):
        self.stream_graph.addNode(node)
        self.graph_heads = [self.stream_graph.getHeadNodeIndex()]
        self.primary_head_idx = 0


    def addSingleOutputStreamNode(self, node: SingleOutputStreamGraphNode):
        # Add a single output stream node to the graph
        self.stream_graph.addNodeToHead(node)
        self.graph_heads = [self.stream_graph.getHeadNodeIndex()]
        self.primary_head_idx = 0
        

    

    # ----------------------------------------------------------------------------------
    def map(self, map_process : Map, process_name: str = None):
        map_node = SingleOutputStreamGraphNode(node_type=SingleOutputStreamGraphNodeType.PROCESS, 
                            process_node_type=SingleOutputStreamGraphNodeProcessType.MAP,
                            node_id=self.streaming_context.getTransformationId(), 
                            name=process_name,
                            node_callable=map_process)
        self.addSingleOutputStreamNode(map_node)
        return self

    def filter(self, filter_process : Filter, process_name: str = None):
        filter_node = SingleOutputStreamGraphNode(node_type=SingleOutputStreamGraphNodeType.PROCESS,
                            process_node_type=SingleOutputStreamGraphNodeProcessType.FILTER,
                            node_id=self.streaming_context.getTransformationId(), 
                            name=process_name,
                            node_callable=filter_process)
        self.addSingleOutputStreamNode(filter_node)
        return self

    # ------------------------------------------------------------------------------------
    def emit(self, emit_process: BaseEmit, emit_name: str = None):
        emit_node = SingleOutputStreamGraphNode(node_type=SingleOutputStreamGraphNodeType.EMIT,
                            node_id=self.streaming_context.getTransformationId(),
                            name=emit_name,
                            node_callable=emit_process)
        self.addSingleOutputStreamNode(emit_node)
        return self

    def setNameOfHead(self, name: str):
        self.stream_graph.setNodeNameOfHead(name)
        return self

    def getNameOfHead(self):
        return self.stream_graph.getNodeNameOfHead()

    def getStreamByNodeName(self, name: str):
        self.stream_graph.setNodeHeadByName(node_name=name)
        return self

    def verifyStreamGraph(self):
        return self.stream_graph.verifyGraph()