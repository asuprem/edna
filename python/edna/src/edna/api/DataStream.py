from __future__ import annotations
from typing import List

from edna.core.plans.streamgraph import StreamGraph
from edna.core.execution.context import StreamingContext

from edna.ingest.streaming import BaseStreamingIngest
from edna.emit import BaseEmit

from edna.core.plans.streamgraph import SingleOutputStreamGraphNode
from edna.types.enums import SingleOutputStreamGraphNodeType
from edna.types.enums import SingleOutputStreamGraphNodeProcessType

from edna.triggers import Trigger

from edna.process.map import Map
from edna.process.filter import Filter
from edna.process.flatten import Flatten
from edna.process.aggregate import Aggregate

class DataStream:
    """DataStream exposes a fluent api for building edna jobs.

    Attributes:
        stream_graph (StreamGraph): The StreamGraph for this DataStream.
        graph_heads (List[int]): The heads for this DataStream within the StreamGraph.
        streaming_context (StreamingContext): The StreamingContext associated with this DataStream
        stream_id (int): The unique id for this DataStream
        datastream_name (str): A name for this DataStream
        primary_head_idx (int): The index of the primary head in `graph_heads`
    """
    stream_graph: StreamGraph
    graph_heads: List[int]
    streaming_context: StreamingContext
    stream_id : int
    datastream_name : str
    primary_head_idx: int


    def __init__(self, ingest: BaseStreamingIngest, streaming_context: StreamingContext, stream_id: int, ingest_name: str = None, datastream_name: str = None):
        """Initialize a DataStream instance with the provided ingest primitive.

        Args:
            ingest (BaseStreamingIngest): An ingest primitive
            streaming_context (StreamingContext): The StreamingContext for this DataStream
            stream_id (int): The id for this DataStream
            ingest_name (str, optional): The name of the ingest node. Defaults to None.
            datastream_name (str, optional): The name of the DataStream. Defaults to None.
        """
        # Build a node with a node-id and node-name
        self.stream_graph = StreamGraph()
        self.graph_heads = []
        self.streaming_context = streaming_context
        self.stream_id = stream_id
        if datastream_name is not None:
            self.datastream_name = datastream_name
        else:
            self.datastream_name = "default"
        self.primary_head_idx = 0
        ingest_node = SingleOutputStreamGraphNode(node_type=SingleOutputStreamGraphNodeType.INGEST, 
                        node_id=self.streaming_context.getNewStreamingNodeId(), name=ingest_name,node_callable=ingest)
        self.addIngestNode(ingest_node)

    def getStreamId(self) -> int:
        """Returns the id of this DataStream

        Returns:
            int: The id of this DataStream
        """
        return self.stream_id
    
    def getStreamName(self) -> str:
        """Returns the name of this DataStream

        Returns:
            str: The name of this DataStream
        """
        return self.datastream_name
    
    def addIngestNode(self, node: SingleOutputStreamGraphNode):
        """Adds the provided ingest node to the DataStream

        Args:
            node (SingleOutputStreamGraphNode): A StreamGraphNode wrapping an ingest primitive
        """
        self.stream_graph.addNode(node)
        self.graph_heads = [self.stream_graph.getHeadNodeIndex()]
        self.primary_head_idx = 0


    def addSingleOutputStreamNode(self, node: SingleOutputStreamGraphNode):
        """Adds a SingleOutputStreamGraphNode to the DataStream, and update the heads.

        Args:
            node (SingleOutputStreamGraphNode): The StreamGraphNode to add
        """
        # Add a single output stream node to the graph
        self.stream_graph.addNodeToHead(node)
        self.graph_heads = [self.stream_graph.getHeadNodeIndex()]
        self.primary_head_idx = 0
        

    

    # ----------------------------------------------------------------------------------
    def map(self, map_process : Map, process_name: str = None) -> DataStream:
        """Adds a Map process primitive to the current head node and returns the DataStream object

        Args:
            map_process (Map): A Map process to add to the DataStream
            process_name (str, optional): The name for this node. Defaults to None.

        Returns:
            DataStream: An updated DataStream instance
        """
        map_node = SingleOutputStreamGraphNode(node_type=SingleOutputStreamGraphNodeType.PROCESS, 
                            process_node_type=SingleOutputStreamGraphNodeProcessType.MAP,
                            node_id=self.streaming_context.getNewStreamingNodeId(), 
                            name=process_name,
                            node_callable=map_process)
        self.addSingleOutputStreamNode(map_node)
        return self

    def filter(self, filter_process : Filter, process_name: str = None) -> DataStream:
        """Adds a Filter process primitive to the current head node and returns the DataStream object

        Args:
            filter_process (Filter): A Filter process to add to the DataStream
            process_name (str, optional): The name for this node. Defaults to None.

        Returns:
            DataStream: An updated DataStream instance
        """
        filter_node = SingleOutputStreamGraphNode(node_type=SingleOutputStreamGraphNodeType.PROCESS,
                            process_node_type=SingleOutputStreamGraphNodeProcessType.FILTER,
                            node_id=self.streaming_context.getNewStreamingNodeId(), 
                            name=process_name,
                            node_callable=filter_process)
        self.addSingleOutputStreamNode(filter_node)
        return self

    def flatten(self, flatten_process : Flatten, process_name: str = None) -> DataStream:
        """Adds a Filter process primitive to the current head node and returns the DataStream object

        Args:
            flatten_process (Flatten): A Flatten process to add to the DataStream
            process_name (str, optional): The name for this node. Defaults to None.

        Returns:
            DataStream: An updated DataStream instance
        """
        flatten_node = SingleOutputStreamGraphNode(node_type=SingleOutputStreamGraphNodeType.PROCESS,
                            process_node_type=SingleOutputStreamGraphNodeProcessType.FLATTEN,
                            node_id=self.streaming_context.getNewStreamingNodeId(), 
                            name=process_name,
                            node_callable=flatten_process)
        self.addSingleOutputStreamNode(flatten_node)
        return self

    def aggregate(self, aggregate_process: Aggregate, trigger_by: Trigger = None, process_name: str = None) -> DataStream:
        if trigger_by is not None:  # Throw error if no trigger???
            aggregate_process.addTrigger(trigger_by)
        aggregate_node = SingleOutputStreamGraphNode(node_type=SingleOutputStreamGraphNodeType.PROCESS,
                            process_node_type=SingleOutputStreamGraphNodeProcessType.AGGREGATE,
                            node_id=self.streaming_context.getNewStreamingNodeId(), 
                            name=process_name,
                            node_callable=aggregate_process)
        self.addSingleOutputStreamNode(aggregate_node)
        return self

    """
    Fort this to work, ????? what to do ???
    def trigger(self, trigger_by: Trigger) -> DataStream:
        if self.stream_graph.getHeadNode().process_node_type == SingleOutputStreamGraphNodeProcessType.AGGREGATE:
            self.stream_graph.getHeadNode().node_callable
    """
    # ------------------------------------------------------------------------------------
    def emit(self, emit_process: BaseEmit, emit_name: str = None) -> DataStream:
        """Adds an emit process primitive to the current head node and returns the DataStream object

        Args:
            emit_process (BaseEmit): An Emit primitive to add to the DataStream
            emit_name (str, optional): The name for this node. Defaults to None.

        Returns:
            DataStream: An updated DataStream instance
        """
        emit_node = SingleOutputStreamGraphNode(node_type=SingleOutputStreamGraphNodeType.EMIT,
                            node_id=self.streaming_context.getNewStreamingNodeId(),
                            name=emit_name,
                            node_callable=emit_process)
        self.addSingleOutputStreamNode(emit_node)
        return self

    def setNameOfHead(self, name: str) -> DataStream:
        """Sets the name of the head node

        Args:
            name (str): The name to set

        Returns:
            DataStream: An updated instance
        """
        self.stream_graph.setNodeNameOfHead(name)
        return self

    def getNameOfHead(self) -> str:
        """Get the name of the head node

        Returns:
            str: The name of the head node
        """
        return self.stream_graph.getNodeNameOfHead()

    def getStreamByNodeName(self, name: str) -> DataStream:
        """Sets the provided name to the head node and returns the DataStream instance

        Args:
            name (str): The name to set for the head

        Returns:
            DataStream: An updated instance
        """
        self.stream_graph.setNodeHeadByName(node_name=name)
        return self

    def verifyStreamGraph(self) -> bool:
        """Verifies the StreamGraph of this DataStream

        Returns:
            bool: Whether the StreamGraph has dangling nodes
        """
        return self.stream_graph.verifyGraph()