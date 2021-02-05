from __future__ import annotations
from edna.core.execution.context import StreamingContext
from edna.core.tasks import SingleSourceSingleTargetTask
from edna.core.plans.physicalgraph import PhysicalGraph
from typing import List, Dict

from edna.core.tasks import TaskPrimitive
from edna.core.plans.physicalgraph import PhysicalGraph
from edna.defaults import EdnaDefault
import time
import logging
from queue import Empty, Queue

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
    task_primitive_nodes: Dict[int,int]
    port_callable: _PortCallable
    task_order: List[int]
    logger: logging.Logger
    message_queue: Queue

    def __init__(self, port_range_min: int = 35000):
        """Initializes an empty ExecutionGraph

        Args:
            port_range_min (int, optional): The minimum port to use. Defaults to 35000. TODO
        """

        self.buffer_emit_addresses = {}
        self.buffer_ingest_addresses = {}
        self.task_primitive_list: List[SingleSourceSingleTargetTask] = []
        self.task_primitive_nodes = {}
        self.task_order = []
        self.tasks_with_buffers = []
        self.tasks_without_buffers = []
        if port_range_min is None:
            self.port_callable = self._EdnaEnginePortCallable()
        else:
            self.port_callable = self._PortCallable(port_range_min)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.message_queue = Queue()
    
    def buildExecutionGraph(self, physical_graph: PhysicalGraph, context: StreamingContext):
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
                self.logger.info("Building Physical Node {node} with ingest-port {ingest} and emit-port {emit}".format(
                    node=physical_graph_node_idx,
                    ingest=ingest_port,
                    emit=emit_port
                ))
                task_primitive_node_id = context.getNewTaskPrimitiveNodeId()
                if task_primitive_node_id in self.task_primitive_nodes:
                    raise RuntimeError("Task node with this id already exists in this ExecutionGraph")
                else:
                    self.logger.info("Mapped Physical node {pnode} to Task Node {tnode}".format(pnode=physical_graph_node_idx, tnode=task_primitive_node_id))
                physical_graph.physical_node_list[physical_graph_node_idx].internal_stream_graph.node_list[0].node_callable.setLoggerWithId(task_primitive_node_id)
                physical_graph.physical_node_list[physical_graph_node_idx].internal_stream_graph.node_list[-1].node_callable.setLoggerWithId(task_primitive_node_id)
                if root_process is not None:
                    root_process.setLoggerWithId(task_primitive_node_id)
                self.task_primitive_list.append(
                    SingleSourceSingleTargetTask(
                        task_node_id=task_primitive_node_id,
                        message_queue=self.message_queue,
                        ingest_primitive=physical_graph.physical_node_list[physical_graph_node_idx].internal_stream_graph.node_list[0].node_callable,
                        emit_primitive=physical_graph.physical_node_list[physical_graph_node_idx].internal_stream_graph.node_list[-1].node_callable,
                        process_primitive=root_process,
                        ingest_port=ingest_port,
                        emit_port=emit_port,
                        max_buffer_size=EdnaDefault.BUFFER_MAX_SIZE,
                        max_buffer_timeout=EdnaDefault.BUFFER_MAX_TIMEOUT_S,
                        logger_name="Task-%i-Primitive"%task_primitive_node_id
                    )
                )
                if ingest_port is not None: # Meaning this task has a buffered_ingest, so needs to be started first...
                    self.tasks_with_buffers.append(len(self.task_primitive_list) - 1 )
                else: # this task has no ingest_port, i.e. regular ingest, i.e. non-blocking, to a degree...
                    self.tasks_without_buffers.append(len(self.task_primitive_list) - 1)
                self.logger.info("Added new Task Primitive Node with: \
                \n\tId: {tnode} \
                \n\tIngest Port: {iport} \
                \n\tEmit Port: {eport} \
                \n\tBuffer Size: {bsize} \
                \n\tBuffer Timeout: {btime} \
                \n\tLogger Name: {lname} \
                \n\tIngest Primitive: {iprim} \
                \n\tEmit Primitive: {eprim} \
                \n\tIngest Serializer: {iser} \
                \n\tIngest Deserializer: {ideser} \
                \n\tEmit Serializer: {eser} ".format(
                    tnode=task_primitive_node_id,iport=ingest_port, eport=emit_port, bsize=EdnaDefault.BUFFER_MAX_SIZE, btime=EdnaDefault.BUFFER_MAX_TIMEOUT_S,lname="Task-%i-Primitive"%task_primitive_node_id,
                    iprim=str(self.task_primitive_list[-1].ingest_primitive),
                    eprim=str(self.task_primitive_list[-1].emit_primitive),
                    iser=str(self.task_primitive_list[-1].ingest_primitive.serializer),
                    ideser=str(self.task_primitive_list[-1].ingest_primitive.serializer.deserializer),
                    eser=str(self.task_primitive_list[-1].emit_primitive.out_serializer)
                ))

                # TODO physical_graph_node_idx is replaced with task_primitive_node_id
                self.task_primitive_nodes[task_primitive_node_id] = 1
        #pdb.set_trace()

        
    def execute(self):
        """Executes the ExecutionGraph's TaskPrimitives
        """
        # Start the thread's activity (where the ingests are blocked...)
        self.logger.info("Building internal processing tasks, if any")
        for task_primitive_idx in self.tasks_with_buffers:
            self.task_primitive_list[task_primitive_idx].start()

        # Start all emits
        self.logger.info("Building emit modules for all tasks")
        for task_primitive in self.task_primitive_list:
            task_primitive.build()


        # Start non-blocking ingests
        self.logger.info("Building ingest tasks")
        for task_primitive_idx in self.tasks_without_buffers:
            self.task_primitive_list[task_primitive_idx].start()
        

        try:
            self.logger.info("All tasks are executing")
            task_nodes_complete = False # This is to poll the queue and check if any of the task nodes have informed us that they are done. If so, we remove them from the list of task nodes
            while not task_nodes_complete:
                time.sleep(EdnaDefault.TASK_POLL_TIMEOUT_S)
                ended_task = None
                try:
                    ended_task = self.message_queue.get(block=True, timeout=EdnaDefault.TASK_POLL_TIMEOUT_S)
                except Empty:
                    ended_task = None
                if ended_task is not None:
                    self.logger.info("Task %i has ended"%ended_task)
                    self.task_primitive_nodes.pop(ended_task, None)
                if len(self.task_primitive_nodes) == 0:
                    self.logger.info("All tasks have ended")
                    task_nodes_complete = True
                     
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received.")    

        self.logger.info("Shutting down tasks.")
        for task_primitive in reversed(self.task_primitive_list):   # TODO bad workaround for the libgcc_s.so.1 must be installed for pthread_cancel to work
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
        