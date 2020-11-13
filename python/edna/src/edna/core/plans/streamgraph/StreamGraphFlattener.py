from __future__ import annotations
from edna.core.plans.streamgraph import StreamGraph

from typing import List, Dict
from edna.api import DataStream

from edna.types.enums import StreamGraphNodeType, SingleOutputStreamGraphNodeProcessType, SingleOutputStreamGraphNodeType

class StreamGraphFlattener:
    """A static class that flattens a collection of streams. Flattening involves
    creating a single StreamGraph out of several Datastreams. During flattening,
    a single unique copy of each node is kept in case of SplitStreams that might
    copy streams lazily.
    """

    @staticmethod
    def flattenStream(stream_collection: Dict[int, DataStream] = None, stream_list: List[DataStream] = None) -> StreamGraph:
        """Flattens a set of Datastreams into a single StreamGraph. Either a dict or list
        can be provided.

        Args:
            stream_collection (Dict[int, DataStream], optional): A collection of `DataStream`s in a 
                dictionary. Defaults to None.
            stream_list (List[DataStream], optional): A list of `DataStream`s. Defaults to None.

        Returns:
            StreamGraph: A flattened StreamGraph.
        """
        if stream_collection is None:
            return StreamGraphFlattener._flatten(stream_list=stream_list)
        return StreamGraphFlattener._flatten(stream_collection.values())

    """
    StreamFlattening:

    iterate through each stream
    for each node in the stream, add it to the streamgraph
        if this node already exists in the streamgraph, don't add it
    for each edge, add that edge to the flattenedStreamGraph
        when we have a splitnode, basically the original streamgraph has a SplitNode, with N connections from it
        case: split as is with emits for each of the N connections. Easy -- just directly copy the nodes
        case: split, with a join down the line that takes in two stream objects (and one of then could technically be split-head)
            in this case, during flattening, we receive the stream after the join, which has a datastream with a join node
            there might be multiple streams
    """


    @staticmethod
    def _flatten(stream_list: List[DataStream]) -> StreamGraph:
        """Flattens a list of datastreams into a single StreamGraph. 

        Args:
            stream_list (List[DataStream]): A list of `DataStream`s

        Returns:
            StreamGraph: A flattened `StreamGraph`
        """
        flattened_stream_graph = StreamGraph()
        # For each stream
        for data_stream in stream_list:
            # For each node in this stream graph
            for stream_graph_node in data_stream.stream_graph.node_list:
                # Check if this node exists in the flattenedStreamGraph. If it does not, add it
                if not flattened_stream_graph.verifyNodeExistsById(stream_graph_node.node_id): 
                    # Depending on the node type, use the appropriate add function   
                    if stream_graph_node.stream_graph_node_type == StreamGraphNodeType.SINGLE_OUTPUT_STREAM:
                        flattened_stream_graph.addNode(stream_graph_node)
                        # Depending on the node type, add a placeholder edge, i.e. only add if ingest or process
                        if stream_graph_node.isIngest() or stream_graph_node.isProcess():
                            flattened_stream_graph.addPlaceholderEdge(flattened_stream_graph.getNodeIndexByNodeId(stream_graph_node.getNodeId()))


            # Now we add the edges to the flattened Stream graph
            for source_node_index in data_stream.stream_graph.node_map:
                source_node_id = data_stream.stream_graph.getNodeByIndex(source_node_index).getNodeId()
                target_node_indexes = data_stream.stream_graph.node_map[source_node_index]

                flattened_source_node_index = flattened_stream_graph.getNodeIndexByNodeId(source_node_id)

                for edge_index, target_node_index in enumerate(target_node_indexes):
                    if target_node_index is None:
                        continue    # None because this is a placeholder. Probably because this is a SplitStream. TODO keep track of this?
                    # target node is a thing, so we update the placeholder stuff
                    target_node_id = data_stream.stream_graph.getNodeByIndex(target_node_index).getNodeId()
                    flattened_target_node_index = flattened_stream_graph.getNodeIndexByNodeId(target_node_id)

                    
                    flattened_stream_graph.updatePlaceholderEdge(flattened_source_node_index, flattened_target_node_index, edge_index)
        
        return flattened_stream_graph


            
                    



