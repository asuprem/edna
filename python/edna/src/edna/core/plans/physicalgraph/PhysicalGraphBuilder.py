


from edna.core.execution.context import StreamingContext

from edna.core.plans.physicalgraph import PhysicalGraph
from edna.core.plans.physicalgraph import PhysicalGraphNode
from edna.core.plans.streamgraph import StreamGraph


class PhysicalGraphBuilder:

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

    @staticmethod
    def convertStreamGraph(stream_graph: StreamGraph, context: StreamingContext) -> PhysicalGraph:
        # For each stream graph node
        physical_graph = PhysicalGraph()
        for stream_graph_node in stream_graph.node_list:
            # Check if node is an ingest. If it is an ingest, we directly create a physical graph node and add it. 
            if stream_graph_node.isIngest():
                physical_graph_node = PhysicalGraphNode(node_id=context.getDatastreamId())
                physical_graph_node.addNode(stream_graph_node=stream_graph_node)
                physical_graph.addPhysicalGraphNode(physical_graph_node)

            elif stream_graph_node.isProcess() or stream_graph_node.isEmit():
                # If process or emit, we 
                pass

            



        