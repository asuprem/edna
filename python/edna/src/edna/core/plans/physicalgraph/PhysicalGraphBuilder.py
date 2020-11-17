from __future__ import annotations
from typing import List


from edna.core.execution.context import StreamingContext

from edna.core.plans.physicalgraph import PhysicalGraph
from edna.core.plans.physicalgraph import PhysicalGraphNode
from edna.core.plans.streamgraph import StreamGraph

from edna.core.plans.streamgraph import SingleOutputStreamGraphNode
from edna.types.enums import SingleOutputStreamGraphNodeType
from edna.types.enums import SingleOutputStreamGraphNodeProcessType

from edna.ingest.streaming._BufferedIngest import _BufferedIngest
from edna.emit._BufferedEmit import _BufferedEmit
from edna.serializers import MsgPackBufferedSerializer


class PhysicalGraphBuilder:
    """PhysicalGraphBuilder builds a PhysicalGraph representing a physical plan for a StreamGraph.
    """

    

    @staticmethod
    def convertStreamGraph(context: StreamingContext) -> PhysicalGraph:
        """Converts a logical plan in the StreamGraph to a PhysicalGraph 
        representing a physical plan .

        Args:
            context (StreamingContext): The context containing the logical plan

        Returns:
            PhysicalGraph: The PhysicalGraph representing the physical plan of
                the logical plan in the provided context
        """
        # For each stream graph node
        physical_graph = PhysicalGraph()
        
        PhysicalGraphBuilder.addNodesAndChildren(context.logical_stream_graph.root_list, physical_graph, context)
        return physical_graph
        

            
    @staticmethod
    def addNodesAndChildren(node_list: List[int], 
                            physical_graph: PhysicalGraph, 
                            context: StreamingContext,
                            parent_node_id : int= None):
        """Recursively adds each StreamGraphNode and its DAG children through a DFS to the PhysicalGraph.

        Args:
            node_list (List[int]): List of indices of each child StreamGraphNode
                for a parent StreamGraphNode in the StreamGraph of the provided context.
            physical_graph (PhysicalGraph): The PhysicalGraph to update
            context (StreamingContext): A `StreamingContext` instance
            parent_node_id (int, optional): The id of the parent StreamGraphNode for each child StreamGraphNode
                in `node_list`. Defaults to None if `node_list` contains root nodes
        """


        for stream_node_idx in node_list:
            #pdb.set_trace()
            # This is an ingest node. We will create a new PhysicalGraphNode.
            if context.logical_stream_graph.node_list[stream_node_idx].isIngest():
                physical_graph_node_id = context.getNewPhysicalNodeId()
                physical_graph.addPhysicalGraphNode(PhysicalGraphNode(node_id=physical_graph_node_id))
                # Then we add nodes to the head...This will also update the dictionaries inside
                physical_graph.insertIngestNodeInHead(context.logical_stream_graph.node_list[stream_node_idx])

            # For an emit node, we will need to first check if the node containing the prior is chainable
            # If not, we need to add a new node
            if context.logical_stream_graph.node_list[stream_node_idx].isEmit():
                # so the prior is represented in parent_node_id...
                #pdb.set_trace()
                if physical_graph.getHeadByStreamNodeId(parent_node_id).isChainable():
                    physical_graph.insertEmitNodeInHead(context.logical_stream_graph.node_list[stream_node_idx])

                else:   # here we need a buffer ingest to point to the parent...
                    # We will need to add an edge, so we need to store the prior physical node id
                    # Note -- how to handle case when the prior node is a split??? TODO later.
                    prior_physical_node_id = physical_graph.getHeadByStreamNodeId(parent_node_id).getPhysicalNodeIdOfHead()
                    physical_graph_node_id = context.getNewPhysicalNodeId()
                    physical_graph.addPhysicalGraphNode(PhysicalGraphNode(node_id=physical_graph_node_id))
                    physical_graph.insertIngestNodeInHead(PhysicalGraphBuilder.buildBufferedIngest(context.getNewStreamingNodeId(), prior_physical_node_id))
                    physical_graph.insertEmitNodeInHead(context.logical_stream_graph.node_list[stream_node_idx])
                    physical_graph.addEdge(prior_physical_node_id, physical_graph_node_id)

            if context.logical_stream_graph.node_list[stream_node_idx].isProcess():
                # If a standard process (not flatten/aggregate)
                create_node_flag = False
                emit_node_flag = False
                if context.logical_stream_graph.node_list[stream_node_idx].process_node_type == SingleOutputStreamGraphNodeProcessType.MAP:
                    if physical_graph.getHeadByStreamNodeId(parent_node_id).isChainable():
                        #pdb.set_trace()
                        physical_graph.insertProcessNodeInHead(context.logical_stream_graph.node_list[stream_node_idx])
                    else:
                        # In this case, it is not chainable so we will create it later
                        create_node_flag = True
                if context.logical_stream_graph.node_list[stream_node_idx].process_node_type == SingleOutputStreamGraphNodeProcessType.FILTER \
                    or context.logical_stream_graph.node_list[stream_node_idx].process_node_type == SingleOutputStreamGraphNodeProcessType.FLATTEN \
                    or context.logical_stream_graph.node_list[stream_node_idx].process_node_type == SingleOutputStreamGraphNodeProcessType.AGGREGATE:
                    # These are pseudoemits
                    emit_node_flag = True
                    if physical_graph.getHeadByStreamNodeId(parent_node_id).isChainable():
                        physical_graph.insertProcessNodeInHead(context.logical_stream_graph.node_list[stream_node_idx])
                    else:
                        create_node_flag = True
                #if context.logical_stream_graph.node_list[stream_node_idx].process_node_type == SingleOutputStreamGraphNodeProcessType.AGGREGATE:
                #    # This is a pseudoingest. So if the prior head is chainable, we need to close it.
                #    if physical_graph.getHeadByStreamNodeId(parent_node_id).isChainable():
                #        physical_graph.insertEmitNodeInHead(PhysicalGraphBuilder.buildBufferedEmit(context.getNewStreamingNodeId()))
                #
                #    else:
                #        create_node_flag = True

                    
                if create_node_flag:
                    # We create a new physical graph node, add a buffered ingest
                    # then we add the stream graph node
                    prior_physical_node_id = physical_graph.getPhysicalNodeIdOfHead()
                    physical_graph_node_id = context.getNewPhysicalNodeId()
                    physical_graph.addPhysicalGraphNode(PhysicalGraphNode(node_id=physical_graph_node_id))
                    physical_graph.insertIngestNodeInHead(PhysicalGraphBuilder.buildBufferedIngest(context.getNewStreamingNodeId(), prior_physical_node_id))
                    physical_graph.insertProcessNodeInHead(context.logical_stream_graph.node_list[stream_node_idx])
                    physical_graph.addEdge(prior_physical_node_id, physical_graph_node_id)


                if emit_node_flag:
                    # we close the current node with a buffer emit
                    physical_graph.insertEmitNodeInHead(PhysicalGraphBuilder.buildBufferedEmit(context.getNewStreamingNodeId()))
                    # TODO add placeholder edge?????

            # If there are children, 

            PhysicalGraphBuilder.addNodesAndChildren(context.logical_stream_graph.getEdgesForNodeIdx(stream_node_idx),physical_graph,context, stream_node_idx)

        #return physical_graph

    @staticmethod
    def buildBufferedIngest(buffered_ingest_node_id: int, receive_from_physical_node_id: int) -> SingleOutputStreamGraphNode:
        """Builds a StreamGraphNode with a `_BufferedIngest` that records some metadata 
        about the source node for this ingest node.

        Args:
            buffered_ingest_node_id (int): A unique node id for this StreamGraphNode
            receive_from_physical_node_id (int): The node id of the PhysicalGraphNode containing
                the parent StreamGraphNode

        Returns:
            SingleOutputStreamGraphNode: A StreamGraphNode containing the `_BufferedIngest`
        """
        return SingleOutputStreamGraphNode(node_type=SingleOutputStreamGraphNodeType.INGEST, 
                        node_id=buffered_ingest_node_id, 
                        name="buffer_ingest", 
                        node_callable=_BufferedIngest(serializer=MsgPackBufferedSerializer(),
                                                      receive_from_node_id=receive_from_physical_node_id))

    @staticmethod
    def buildBufferedEmit(buffered_emit_node_id: int) -> SingleOutputStreamGraphNode:
        """Builds a StreamGraphNode with a `_BufferedEmit` that records some metadata 
        about the source node for this ingest node.

        Args:
            buffered_emit_node_id (int): A unique node id for this StreamGraphNode

        Returns:
            SingleOutputStreamGraphNode: A StreamGraphNode containing the `_BufferedEmit`
        """
        return SingleOutputStreamGraphNode(node_type=SingleOutputStreamGraphNodeType.EMIT,
                            node_id=buffered_emit_node_id,
                            name="buffer_emit",
                            node_callable=_BufferedEmit(serializer=MsgPackBufferedSerializer()))    #TODO add constants for batch size...

"""
completed_nodes = {}
StreamGraphToPhysicalGraphNodeDictioanry = {}
PhysicalIdsToPhysicalNodeDictionary = {}
BufferEdges = {}
JoinPlaceholders = {}
addNodesAndChildren(streamgraph.root_nodes, root=None)

>addNodesAndChildren(node_list, root_node_id):
for each stream_graph_node in root_nodes:
    #stream_graph_node_type = StreamGraphNodeType.SINGLE_OUTPUT_STREAM (or split, join)
    #process_node_type=SingleOutputStreamGraphNodeProcessType.FILTER,
    - if stream_graph_node.isIngest()
        - get new physical graph node id
        - create a new PhysicalGraphNode(ingestNode)
        - add to PhysicalIdsToPhysicalNodeDictionary --> {physical_graph_node.node_id = PhysicalGraphNode}
        - add to StreamGraphToPhysicalGraphNodeDictionary ->  {stream_graph_node.node_id = physical_graph_node.node_id}

    - if stream_graph_node.isEmit():
        physical_graph_node_id = StreamGraphToPhysicalGraphNodeDictionary[root_node_id]
        if getPhysicalNodeFromId(physical_graph_node_id).isChainable():
            getPhysicalNodeFromId(physical_graph_node_id).addStreamGraphNode(stream_graph_node)
            getPhysicalNodeFromId(physical_graph_node_id).setIsNotChainable()
        else:
            get new physical graph node id
            create a new PhysicalGraphNode(bufferIngest)
            add to PhysicalIdsToPhysicalNodeDictionary --> {physical_graph_node.node_id = PhysicalGraphNode}
            add to StreamGraphToPhysicalGraphNodeDictionary ->  {stream_graph_node.node_id = physical_graph_node.node_id}
            parent_physical_graph_node_id = StreamGraphToPhysicalGraphNodeDictionary[root_node_id]
            BufferEdges[parent_physical_graph_node_id].append(physical_graph_node_id)
            getPhysicalNodeFromId(physical_graph_node_id).addStreamGraphNode(stream_graph_node)
            getPhysicalNodeFromId(physical_graph_node_id).setIsNotChainable()
            # THIS IS NOT NEEDED --> BufferEdges[parent_physical_graph_node_id] = [] <-- BECAUSE THIS IS EMIT NODE


    - if stream_graph_node.isProcess():
        create_node_flag = False
        emit_node_flag = False
        if stream_graph_node.process_node_type == SingleOutputStreamGraphNodeProcessType.MAP:
            physical_graph_node_id = StreamGraphToPhysicalGraphNodeDictionary[root_node_id]
            if getPhysicalNodeFromId(physical_graph_node_id).isChainable():
                getPhysicalNodeFromId(physical_graph_node_id).addStreamGraphNode(stream_graph_node)
            else:
                create_node_flag = True # we will create node later below
        elif FILTER:    # this is a sink node
            physical_graph_node_id = StreamGraphToPhysicalGraphNodeDictionary[root_node_id]
            if getPhysicalNodeFromId(physical_graph_node_id).isChainable():
                getPhysicalNodeFromId(physical_graph_node_id).addStreamGraphNode(stream_graph_node)
                getPhysicalNodeFromId(physical_graph_node_id).addStreamGraphNode(buffer_emit)   # basically a pseudonode that just tells executionplancreator in the future that this is a buffer_emit
                getPhysicalNodeFromId(physical_graph_node_id).setIsNotChainable()
            else:
                create_node_flag = True
                emit_node_flag = True
        elif FLATTEN: # this is also a sink node
            physical_graph_node_id = StreamGraphToPhysicalGraphNodeDictionary[root_node_id]
            if getPhysicalNodeFromId(physical_graph_node_id).isChainable():
                getPhysicalNodeFromId(physical_graph_node_id).addStreamGraphNode(stream_graph_node)
                getPhysicalNodeFromId(physical_graph_node_id).addStreamGraphNode(buffer_emit)
                getPhysicalNodeFromId(physical_graph_node_id).setIsNotChainable()
            else:
                create_node_flag = True
                emit_node_flag = True
        elif AGGREGATE: # this is a source node, so we have to check if the parent is chainable. if so, we need to add the emit to it.
            physical_graph_node_id = StreamGraphToPhysicalGraphNodeDictionary[root_node_id]
            if getPhysicalNodeFromId(physical_graph_node_id).isChainable():
                getPhysicalNodeFromId(physical_graph_node_id).addStreamGraphNode(stream_graph_node)
                getPhysicalNodeFromId(physical_graph_node_id).addStreamGraphNode(buffer_emit)
                getPhysicalNodeFromId(physical_graph_node_id).setIsNotChainable()
            else:
                create_node_flag = True
                emit_node_flag = True
        else:
            raise NotImplementedError()

        if create_node_flag:
            get new physical graph node id
            create a new PhysicalGraphNode(bufferIngest)
            add to PhysicalIdsToPhysicalNodeDictionary --> {physical_graph_node.node_id = PhysicalGraphNode}
            add to StreamGraphToPhysicalGraphNodeDictionary ->  {stream_graph_node.node_id = physical_graph_node.node_id}
            parent_physical_graph_node_id = StreamGraphToPhysicalGraphNodeDictionary[root_node_id]
            BufferEdges[parent_physical_graph_node_id].append(physical_graph_node_id)
            if emit_node_flag:
                getPhysicalNodeFromId(physical_graph_node_id).addStreamGraphNode(stream_graph_node)
                getPhysicalNodeFromId(physical_graph_node_id).addStreamGraphNode(buffer_emit)
                getPhysicalNodeFromId(physical_graph_node_id).setIsNotChainable()
                BufferEdges[parent_physical_graph_node_id] = []



    - if stream_graph_node.isSplit()    # This is an emit (ish)
        physical_graph_node_id = StreamGraphToPhysicalGraphNodeDictionary[root_node_id]
        if not getPhysicalNodeFromId(physical_graph_node_id).isChainable():
            physical_graph_node_id = get new physical graph node id
            create a new PhysicalGraphNode(bufferIngest)
            add to PhysicalIdsToPhysicalNodeDictionary --> {physical_graph_node.node_id = PhysicalGraphNode}
            add to StreamGraphToPhysicalGraphNodeDictionary ->  {stream_graph_node.node_id = physical_graph_node.node_id}
            parent_physical_graph_node_id = StreamGraphToPhysicalGraphNodeDictionary[root_node_id]
            BufferEdges[parent_physical_graph_node_id].append(physical_graph_node_id)

        if getPhysicalNodeFromId(physical_graph_node_id).isChainable(): # This is a sink node, btw...
            getPhysicalNodeFromId(physical_graph_node_id).addSplitStreamGraphNode(stream_graph_node)
            getPhysicalNodeFromId(physical_graph_node_id).addStreamGraphNode(split_buffer_emit) # basically tell executionbuilder that this physicalgraphnode ends in a splitnode, so that we can build the correct task primitive
            getPhysicalNodeFromId(physical_graph_node_id).setIsNotChainable()
            BufferEdges[parent_physical_graph_node_id] = []

    - if stream_graph_node.isJoin(): This is a source (ish)
        physical_graph_node_id = StreamGraphToPhysicalGraphNodeDictionary[root_node_id]
        if getPhysicalNodeFromId(physical_graph_node_id).isChainable():
            getPhysicalNodeFromId(physical_graph_node_id).addStreamGraphNode(buffer_emit)
            getPhysicalNodeFromId(physical_graph_node_id).setIsNotChainable()
            BufferEdges[parent_physical_graph_node_id] = []
        
        physical_graph_node_id = get new physical graph node id
        create a new PhysicalGraphNode(joinIngest)  # joinIngest takes in the stream_node_ids of the parents. This should already be present inside the node, actually
        add to PhysicalIdsToPhysicalNodeDictionary --> {physical_graph_node.node_id = PhysicalGraphNode}
        add to StreamGraphToPhysicalGraphNodeDictionary ->  {stream_graph_node.node_id = physical_graph_node.node_id}
        for # TODO later. basically we need a way to identify where the joins are coming from, i.e. to specifically idetify which port of which physicalgraphnode it is comingn from
            - example -- when join comes from one of the splits of a node, how to represent this???
            - Somehow need to deal with the `snafu` of DataStream and SplitStream...





    completed_nodes.add(stream_graph_node.node_id)
    BufferEdges[stream_graph_node.node_id] = []
        # Node, we need a secondary buffer to store bufferedgees for joinnodes where we haven't yet added the second stream...
    addNodesAndChildren(stream_graph_node.getChildren(), stream_graph_node.node_id)

    







"""

"""This represents a physical graph of physical graph nodes
    Physical graph nodes contain streamgraphnodes in a physicalnodegraph.
        Physicalnodegraphs are DAGS with no branching (except in the leaf) 
        root - internal - internal - leaf

        physical graph iterates through nodes in streamgraph
            for each node, check if it is a join node
                if so, create a new physicalnode with it, and store the edges to its previous physicalnodes (which we can get with our streamgraphnode-to-physicalnode dictionary)
            if not join, then check which single node it connects to and the associated physicalnode
            check if this node can be added to the physicalnode. if so, update the streamgraphnode-to-physicalnode dictionary
            if node, create a physicalnode with it
                physicalnode returns a node wrapping the streamgraphnode
                physicalnode returns a specific type of node given the streamgraphnode it was just given
                    singleoutputnode -- we can add new nodes to it (it can have a join, emit, or process as the root node)
                    splitoutputnode -- we cannot add new nodes to it (it can have a join, emit, or process as the root node)

            add this physicalnode to the physicalgraph
            add an edge between this physicalnode and the previous physicalnode

"""