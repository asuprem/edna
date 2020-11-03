from __future__ import annotations
from typing import Dict
import warnings

from edna.api import DataStream

from edna.core.execution.context import EdnaContext
from edna.core.configuration import StreamingConfiguration

from edna.core.plans.streamgraph import StreamGraph
from edna.core.plans.streamgraph import StreamGraphFlattener

from edna.core.plans.physicalgraph import PhysicalGraph
from edna.core.plans.physicalgraph import PhysicalGraphBuilder

import pdb

class StreamingContext(EdnaContext):
    transformation_id : int = -1 # Running count of transformation ids
    physical_node_id : int = -1
    datastream_id : int = -1
    stream_collection : Dict[int, DataStream] = {}
    stream_graph: StreamGraph = None

    logical_stream_graph : StreamGraph
    physical_graph : PhysicalGraph
    # physical_stream_graph
    # execution_graph

    def __init__(self, dir : str = ".", confpath : str = "ednaconf.yaml", confclass: StreamingConfiguration = StreamingConfiguration):
        super().__init__(dir=dir, confpath=confpath, confclass=confclass)

        self.transformation_id = -1
        self.physical_node_id = -1
        self.datastream_id = -1
        self.stream_collection = {}
        self.stream_graph = None


    def getTransformationId(self):
        self.transformation_id += 1
        return self.transformation_id
    
    def getDatastreamId(self):
        self.datastream_id += 1
        return self.datastream_id

    def getPhysicalNodeId(self):
        self.physical_node_id += 1
        return self.physical_node_id

    def addStream(self, stream: DataStream):
        if not stream.verifyStreamGraph():
            # TODO handle wanring
            warnings.warn("Stream graph might not be valid. Probably because SplitStream has Nones")
        if stream.getStreamId() in self.stream_collection:
            raise RuntimeError("Stream already exists in current context.")
        self.stream_collection[stream.getStreamId()] = stream

    
    def run(self):
        """Steps:

        1. First flatten the streams
        2. Then convert the streamgraph to a physicalgraph
        3. Then convert the physicalgraph to an executiongraph, and start an executioncontext
        4. Execute the executioncontext (I Guess)
        """
        
        #pdb.set_trace()
        self.logical_stream_graph = self.flattenStream()
        pdb.set_trace()
        self.physical_graph = self.buildPhysicalGraph()


        # TODO
        # Then convert to physical graph
        # Convert the chained nodes that are 1-1 into a single node (we will deal with specifics later)
        # Add buffer nodes between single nodes -- basically replace each edge with a write buffer and a read buffer.
        # A write buffer and a read buffer next to each other have the same port

        # Physical graph conversion -- take all edges where the source and target are process nodes and source is a MAP process
            # replace with a ChainedProcess, which is a BaseProcess that takes an outer and inner, and does outer(inner())
            # Also need to handle ingest-process pairs, and process-emit pairs
            # Then we need to handle serializers serializers

        
        # So we will use breadth first.
        # We need a PhysicalPrimitive.


    def flattenStream(self) -> StreamGraph:
        """flattenStream() will combine all the stream graphs into a single graph
        TODO when we add SplitStreamOperator, we will need to update this flattenStream()
        """
        return StreamGraphFlattener.flattenStream(self.stream_collection)

        
        # First add each node to the flattenedStreamGraph
    
    def buildPhysicalGraph(self) -> PhysicalGraph:
        return PhysicalGraphBuilder.convertStreamGraph(self.logical_stream_graph, self)