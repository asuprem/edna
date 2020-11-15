from __future__ import annotations
from edna.core.tasks import SingleSourceSingleTargetTask
from edna.core.plans.physicalgraph import PhysicalGraph
from typing import List, Dict

from edna.core.tasks import TaskPrimitive
from edna.core.plans.physicalgraph import PhysicalGraph
from edna.defaults import EdnaDefault
import time
import logging


class ExecutionGraph:
    """ExecutionGraph represents the actual executable components of an Edna Job. 
    Each node of an ExecutionGraph is an edna.core.tasks.TaskPrimitive build from
    the nodes of a PhysicalGraph.

    Attributes:
        task_primitive_list (List[TaskPrimitive]): List of Task Primitives
        buffer_emit_addresses (Dict[int,int]): Stores the edges for
            a TaskPrimitive to track addresses for the emits
        buffer_ingest_addresses (Dict[int,int]): Stores the edges for
            a TaskPrimitive to track addresses for the ingests
        port_callable (_PortCallable): The port callable to generate new
            addresses for each TaskPrimitive, if needed.
        task_order (List[int]): The task order for launching the TaskPrimitives
        logger (logging.Logger): The logger for this ExecutionGraph
    """
    task_primitive_list: List[TaskPrimitive]
    buffer_emit_addresses: Dict[int,int]
    buffer_ingest_addresses: Dict[int,int]
    port_callable: _PortCallable
    task_order: List[int]
    logger: logging.Logger

    def __init__(self, port_range_min: int = 35000):
        """Initializes an empty ExecutionGraph

        Args:
            port_range_min (int, optional): The minimum port to use. Defaults to 35000. TODO
        """

        self.buffer_emit_addresses = {}
        self.buffer_ingest_addresses = {}
        self.task_primitive_list = []
        self.task_order = []
        if port_range_min is None:
            self.port_callable = self._EdnaEnginePortCallable()
        else:
            self.port_callable = self._PortCallable(port_range_min)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def buildExecutionGraph(self, physical_graph: PhysicalGraph):
        """Converts a PhysicalGraph to TaskPrimitives in an ExecutionGraph

        Args:
            physical_graph (PhysicalGraph): The PhysicalGraph to convert
        """
        self.logger.debug("Populating Buffer addresses for ExecutionGraph")
        self.populateBufferAddresses(physical_graph)
        self.task_order = self.buildDepthOrder(physical_graph)

        for physical_graph_node_idx in self.task_order:
            # Single Source Single Target

            if physical_graph.physical_node_list[physical_graph_node_idx].internal_stream_graph.node_list[0].isIngest() and \
                physical_graph.physical_node_list[physical_graph_node_idx].internal_stream_graph.node_list[-1].isEmit():
                # Build process:
                ingest_port = self.buffer_ingest_addresses.get(physical_graph.physical_node_list[physical_graph_node_idx].node_id, None)
                emit_port = self.buffer_emit_addresses.get(physical_graph.physical_node_list[physical_graph_node_idx].node_id, None)
                root_process = None
                for base_process_nodes in physical_graph.physical_node_list[physical_graph_node_idx].internal_stream_graph.node_list[1:-1]:
                    base_process_nodes.node_callable.replaceChainedProcess(root_process)
                    # del root_process
                    root_process = base_process_nodes.node_callable
                self.logger.info("Building Task Node {node} with ingest-port {ingest} and emit-port {emit}".format(
                    node=physical_graph_node_idx,
                    ingest=ingest_port,
                    emit=emit_port
                ))
                self.task_primitive_list.append(
                    SingleSourceSingleTargetTask(ingest_primitive=physical_graph.physical_node_list[physical_graph_node_idx].internal_stream_graph.node_list[0].node_callable,
                        emit_primitive=physical_graph.physical_node_list[physical_graph_node_idx].internal_stream_graph.node_list[-1].node_callable,
                        process_primitive=root_process,
                        ingest_port=ingest_port,
                        emit_port=emit_port,
                        max_buffer_size=EdnaDefault.BUFFER_MAX_SIZE,
                        max_buffer_timeout=EdnaDefault.BUFFER_MAX_TIMEOUT_S,
                        logger_name="TaskPrimitive-For-TaskNode-"+str(physical_graph_node_idx)
                    )
                )
        #pdb.set_trace()

        
    def execute(self):
        """Executes the ExecutionGraph's TaskPrimitives
        """
        for task_primitive in self.task_primitive_list:
            task_primitive.start()

        for task_primitive in self.task_primitive_list:
            task_primitive.build()

        try:
            self.logger.info("All tasks are executing")
            while True:
                time.sleep(EdnaDefault.TASK_POLL_TIMEOUT_S)
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received. Shutting down tasks")
            for task_primitive in self.task_primitive_list:
                task_primitive.stop()
            self.logger.info("Rejoining main thread")
            for task_primitive in self.task_primitive_list:
                task_primitive.join()
        self.logger.info("Finished Execution")


    def populateBufferAddresses(self, physical_graph: PhysicalGraph):
        """Generates and populates buffer addresses for each edge in the PhysicalGraph

        Args:
            physical_graph (PhysicalGraph): The PhysicalGraph to use to 
                generate the buffer addresses.
        """
        for source_node_id in physical_graph.physical_nodes_edges:
            port = self.port_callable.requestNewPort()
            self.buffer_emit_addresses[source_node_id] = port
            for target_node_id in physical_graph.physical_nodes_edges[source_node_id]:
                self.buffer_ingest_addresses[target_node_id] = port

    def buildDepthOrder(self, physical_graph: PhysicalGraph) -> List[int]:
        """Builds the order for the TaskPrimitive. During launch, execution
        graph nodes are executed in leaf-first order. 

        Args:
            physical_graph (PhysicalGraph): The PhysicalGraph to use to build the depth order.

        Returns:
            List[int]: Returns the order of task primitives, referenced by the physical node ids
        """
        # Arrange the physical nodes in reverse depth order
        depth_order = {}
        self._dfsDepth(depth_order, physical_graph.physical_node_root_list, physical_graph, None)
        return [item[0] for item in sorted(depth_order.items(), key=lambda x:x[1],reverse=True)]

    def _dfsDepth(self,depth_order:Dict[int,int], node_idx_list, physical_graph: PhysicalGraph,parent_node_idx:int = None):
        """Recursive function to order physical graph nodes by their depth in the graph

        Args:
            depth_order (Dict[int,int]): The depth order so far.
            node_idx_list (List[int]): List of nodes to process
            physical_graph (PhysicalGraph): The PhysicalGraph instance to explore in DFS order
            parent_node_idx (int, optional): The index of the parent PhysicalGraphNode. Defaults to None.
        """
        for physical_graph_node_idx in node_idx_list:
            if physical_graph_node_idx not in depth_order:
                depth_order[physical_graph_node_idx] = 0

            if parent_node_idx is None: # is root
                depth_order[physical_graph_node_idx] = 0
            else:
                temp_depth = depth_order[parent_node_idx]+1
                if temp_depth > depth_order[physical_graph_node_idx]:
                    depth_order[physical_graph_node_idx] = temp_depth
            
            self._dfsDepth(depth_order,physical_graph.getEdgesForPhysicalNodeIdx(physical_graph_node_idx), physical_graph, physical_graph_node_idx)


    class _PortCallable:
        def __init__(self,port_range_min: int):
            self.port = port_range_min

        def requestNewPort(self):
            self.port += 1
            return self.port - 1

    class _EdnaEnginePortCallable:
        def __init__(self):
            raise NotImplementedError()

        def requestNewPort(self):
            raise NotImplementedError()
        