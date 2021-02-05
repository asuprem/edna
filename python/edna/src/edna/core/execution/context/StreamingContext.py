from __future__ import annotations
from typing import Dict

from edna.api import DataStream

from edna.core.execution.context import EdnaContext
from edna.core.configuration import StreamingConfiguration

from edna.core.plans.streamgraph import StreamGraph
from edna.core.plans.streamgraph import StreamGraphFlattener

from edna.core.plans.physicalgraph import PhysicalGraph
from edna.core.plans.physicalgraph import PhysicalGraphBuilder
from edna.core.plans.executiongraph import ExecutionGraph

class StreamingContext(EdnaContext):
    """StreamingContext executes Edna Jobs in a pipelined fashion. Records are 
    processed 1-at-a-time (but are batched during emitting to increase throughput 
    of network buffers). 

    The relevant methods are:

        - `addStream()`: Add a new DataStream to the context. The DataStream should be a completed
            stream with no dangling nodes.
        - `execute()`: This executes the context by first optimizing the DataStream job graph and then 
            generative executable TaskPrimitives

    Attributes:
        streaming_node_id (int): Keeps track of unique StreamGraphNode ids for this context
        physical_node_id (int) : Keeps track of unique PhysicalGraphNode ids for this context
        datastream_id (int): Keeps track of unique DataStream ids for this context
        stream_collection (Dict[int, DataStream]): Collection of DataStreams added to this context
        logical_stream_graph (StreamGraph): The StreamGraph for this context
        physical_graph (PhysicalGraph): The PhysicalGraph for this context
        execution_context (ExecutionGraph): The ExecutionGraph for this context
    """
    
    streaming_node_id : int # Running count of stream node ids
    physical_node_id : int # Running count of physical node ids
    datastream_id : int # Running count of streams
    task_primitive_id : int
    stream_collection : Dict[int, DataStream]
    logical_stream_graph : StreamGraph
    physical_graph : PhysicalGraph
    execution_context: ExecutionGraph
    # physical_stream_graph
    # execution_graph

    def __init__(self, dir : str = ".", 
                    confpath : str = "ednaconf.yaml", 
                    confclass: StreamingConfiguration = StreamingConfiguration):
        """Initializes the StreamingContext

        Args:
            dir (str, optional): The directory that contains the configuration for this context. Defaults to ".".
            confpath (str, optional): The path to the edna configuration file `ednaconf.yaml`. Defaults to "ednaconf.yaml".
            confclass (StreamingConfiguration, optional): The configuration format class for this context. Defaults to StreamingConfiguration.
        """
        super().__init__(dir=dir, confpath=confpath, confclass=confclass, logger="StreamingContext")
        self.streaming_node_id = -1
        self.physical_node_id = -1
        self.datastream_id = -1
        self.task_primitive_id = -1
        self.stream_collection = {}
        self.logical_stream_graph = None
        self.physical_graph = None
        self.execution_context = None
        self.logger.info("Initialized the Streaming Context")


    def getNewStreamingNodeId(self) -> int:
        """Get a new unique node id for a StreamGraphNode

        Returns:
            int: A unique node id
        """
        self.streaming_node_id += 1
        self.logger.debug("New streamgraph node id requested: {streaming_node_id}".format(streaming_node_id=self.streaming_node_id))
        return self.streaming_node_id
    
    def getDatastreamId(self) -> int:
        """Get a new unique id for a DataStream

        Returns:
            int: A unique id
        """
        self.datastream_id += 1
        self.logger.debug("New datastream id requested: {datastream_id}".format(datastream_id=self.datastream_id))
        return self.datastream_id

    def getNewPhysicalNodeId(self) -> int:
        """Get a new unique id for a PhysicalGraphNode

        Returns:
            int: A unique node id
        """
        self.physical_node_id += 1
        self.logger.debug("New physical node id requested: {physical_node_id}".format(physical_node_id=self.physical_node_id))
        return self.physical_node_id

    def getNewTaskPrimitiveNodeId(self) -> int:
        self.task_primitive_id += 1
        self.logger.debug("New task primitive node id requested: {task_node_id}".format(task_node_id=self.task_primitive_id))
        return self.task_primitive_id

    def addStream(self, stream: DataStream):
        """Add a DataStream to this context

        Args:
            stream (DataStream): A DataStream to add to this context

        Raises:
            RuntimeError: Raised if the DataStream already exists in `stream_collection`
        """
        if not stream.verifyStreamGraph():
            # TODO handle wanring
            self.logger.warn("Stream graph might not be valid. Probably because SplitStream has Nones")
        if stream.getStreamId() in self.stream_collection:
            # TODO log to error?
            raise RuntimeError("Stream already exists in current context.")
        self.logger.info("Adding new stream to context with stream name {stream_name} and stream id {stream_id}"
            .format(stream_name=stream.getStreamName(), 
                    stream_id=stream.getStreamId()))
        self.stream_collection[stream.getStreamId()] = stream

    
    def run(self):
        """Executes this context.

            1. First flattens the DataStreams to a logical StreamGraph with a `StreamGraphFlattener`
            2. Converts the logical StreamGraph to a PhysicalGraph with a `PhysicalGraphBuilder`
            3. Converts the PhysicalGraph to an ExecutionGraph, with TaskPrimitives for each PhysicalGraphNode
            4. Executes the TaskPrimitives in the ExecutionGraph
        """
        
        self.logger.info("Starting context execution")
        #pdb.set_trace()

        self.logger.info("Flattening streams to StreamGraph")
        self.logical_stream_graph = self.flattenStream()
        # TODO we need to delete the old stream graphs
        # Also, need to make sure when we add the stream nodes to the flattened stream, we pass by reference and only delete
        #     the collection of streams, not the actual nodes.
        #     TODO TODO Also, need to adjust the initialization functions of each node so that it does lazy initialization!!!!
        self.logger.info("Flattened {num_streams} into single stream".format(num_streams=len(self.stream_collection)))
        #pdb.set_trace()

        
        self.logger.info("Converting StreamGraph to PhysicalGraph")
        self.physical_graph = self.buildPhysicalGraph()
        self.logger.info("Converted StreamGraph with {num_nodes} nodes to PhysicalGraph with {num_phys} PhysicalNodes".format(
            num_nodes=len(self.logical_stream_graph.node_list),
            num_phys = len(self.physical_graph.physical_node_list)
        ))
        #pdb.set_trace()

        self.execution_context = ExecutionGraph()
        self.logger.info("Converting PhysicalGraph to ExecutionGraph")
        self.execution_context.buildExecutionGraph(self.physical_graph, self)
        #pdb.set_trace()

        self.logger.info("Executing the context")
        execution = self.execution_context.execute()
        self.logger.info("Finished executing context")
        

    def flattenStream(self) -> StreamGraph:
        """Calls `StreamGraphFlattener` to flatten the `stream_collection` to a `StreamGraph`

        Returns:
            StreamGraph: A flattened logical `StreamGraph`
        """
        return StreamGraphFlattener.flattenStream(self.stream_collection)

        
        # First add each node to the flattenedStreamGraph
    
    def buildPhysicalGraph(self) -> PhysicalGraph:
        """Converts the logical `StreamGraph` to a `PhysicalGraph`

        Returns:
            PhysicalGraph: A PhysicalGraph
        """
        return PhysicalGraphBuilder.convertStreamGraph(self)