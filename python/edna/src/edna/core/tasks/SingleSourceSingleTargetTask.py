from __future__ import annotations
from edna.types.builtin import StreamElement
from edna.types.builtin import RecordCollection
from queue import Queue
from typing import Dict
import time
from concurrent.futures.thread import ThreadPoolExecutor
from edna.core.tasks.TaskPrimitive import TaskPrimitive
from edna.types.enums import EmitPattern
from edna.types.enums import IngestPattern
from edna.ingest.streaming import BaseStreamingIngest
from edna.process import BaseProcess
from edna.emit import BaseEmit
from edna.defaults import EdnaDefault


class SingleSourceSingleTargetTask(TaskPrimitive):
    """A SingleSourceSingleTargetTask has a single input and single output stream.

    Attributes:
        ingest_primitive (BaseStreamingIngest): The ingest primitive for this SingleSourceSingleTargetTask
        emit_primitive (BaseEmit): The emit primitive for this SingleSourceSingleTargetTask
        process_primitive (BaseProcess): The process primitive for this SingleSourceSingleTargetTask
        ingest_build_configuration (Dict[str,str]): The build configuration for the ingest primitive,
            for lazy building.
        emit_build_configuration (Dict[str,str]): The build configuration for the emit primitive,
            for lazy building.
    """
    ingest_primitive: BaseStreamingIngest
    emit_primitive: BaseEmit
    process_primitive: BaseProcess
    ingest_executor: ThreadPoolExecutor
    ingest_build_configuration: Dict[str,str]
    emit_build_configuration: Dict[str,str]

    def __init__(self, 
            task_node_id: int,
            message_queue: Queue,
            ingest_primitive: BaseStreamingIngest,
            emit_primitive: BaseEmit,
            process_primitive: BaseProcess = None,
            ingest_port : int = None,
            emit_port : int = None, 
            max_buffer_size : int = EdnaDefault.BUFFER_MAX_SIZE, 
            max_buffer_timeout : float = EdnaDefault.BUFFER_MAX_TIMEOUT_S,
            logger_name: str = None):
        """Initialize a SingleSourceSingleTargetTask with the provided primitives 
        and build configuration parameters, if needed, for buffered ingests and emits.

        Args:
            ingest_primitive (BaseStreamingIngest): The ingest primitive for this TaskPrimitive.
            emit_primitive (BaseEmit): The emit primitive for this TaskPrimitive
            process_primitive (BaseProcess, optional): The process primitive for this TaskPrimitive. Defaults to None.
            ingest_port (int, optional): The ingest port if this Task has a `_BufferedIngest`. Defaults to None.
            emit_port (int, optional): The emit port if this Task has a `_BufferedEmit`. Defaults to None.
            max_buffer_size (int, optional): The maximim size for the network buffer. Defaults to EdnaDefault.BUFFER_MAX_SIZE.
            max_buffer_timeout (float, optional): The maximim timeout for the network buffer. Defaults to EdnaDefault.BUFFER_MAX_TIMEOUT_S.
            logger_name (str, optional): The name for this TaskPrimitive's logger. Defaults to None.
        """
        super().__init__(task_node_id=task_node_id, message_queue=message_queue, max_buffer_size=max_buffer_size, max_buffer_timeout=max_buffer_timeout, logger_name=logger_name)
        # Set up process primitive
        self.process_primitive = process_primitive if process_primitive is not None else lambda x: x
        # Set up ingest port or primitive
        self.ingest_primitive = ingest_primitive        
        # Set up emit port and primitive
        self.emit_primitive = emit_primitive
        # Set up ingest executor thread
        self.ingest_executor = ThreadPoolExecutor(max_workers=1)
        # If it is a buffered ingest, we set up the buffered downloaders
        self.ingest_build_configuration = {}
        if self.ingest_primitive.execution_mode == IngestPattern.BUFFERED_INGEST:
            # TODO else if standard ingest, use the provided build configuration...probably empty?
            self.ingest_build_configuration["ip"] = EdnaDefault.TASK_PRIMITIVE_HOST
            self.ingest_build_configuration["ingest_port"] = ingest_port
            self.ingest_build_configuration["max_buffer_size"] = self.MAX_BUFFER_SIZE
            self.ingest_build_configuration["max_buffer_timeout"] = self.MAX_BUFFER_TIMEOUT_S
            
        
        # Set up emits (standard emit is already set up earlier...)
        self.emit_build_configuration = {}
        if self.emit_primitive.emit_pattern == EmitPattern.BUFFERED_EMIT:
            self.emit_build_configuration["ip"] = EdnaDefault.TASK_PRIMITIVE_HOST_NAME
            self.emit_build_configuration["emit_port"] = emit_port
            self.emit_build_configuration["max_buffer_size"] = self.MAX_BUFFER_SIZE
            self.emit_build_configuration["max_buffer_timeout"] = self.MAX_BUFFER_TIMEOUT_S

    def build(self):
        """Builds the emit primitive. 
        """
        self.logger.info("Building Task Node emit connections")
        self.emit_primitive.build(self.emit_build_configuration)
        self.logger.info("Built Emit Primitive")

    def buildIngest(self):
        """Builds the ingest primitive
        """
        self.logger.info("Building Task Node ingest connections")
        self.ingest_primitive.build(self.ingest_build_configuration)
        self.logger.info("Built Ingest Primitive")    

    def run(self):
        """Builds the ingest primitive, then begins executing the task.
        """
        self.buildIngest()
        self.logger.info("Starting Task execution")
        # Used to collect the record future object, poll it, and process it when it is available
        record_future = None    
        # Used to check if a shutdown has been applied through a shutdown emit. If so, flush and shut down.
        shutdown_flag = False
        # Processing flag is set when the record future is not yet available.
        processing_flag = False

        while self.running() and not shutdown_flag:
            if record_future is None and not processing_flag:
                record_future = self.ingest_executor.submit(next,self.ingest_primitive)
                processing_flag = True
            if record_future.done():
                processing_flag = False
                streaming_records:RecordCollection[StreamElement] = record_future.result()
                self.logger.debug("Received  --> %s"%str([(type(item), item.getValue()) for item in streaming_records]))
                intermediate_record = self.process_primitive(streaming_records)
                self.logger.debug("Processed --> %s"%str([(type(item), item.getValue()) for item in intermediate_record]))
                shutdown_flag = self.emit_primitive(intermediate_record)
                record_future = None
                self.emit_primitive.checkBufferTimeout()
            if shutdown_flag:
                self.logger.debug("Stream has ended. Setting shutdown signal in Task Node and flushing")
                self.emit_primitive.flush()
            self.emit_primitive.checkBufferTimeout()
        if not self.running() and not shutdown_flag:
            self.logger.info("Task shutdown requested")
        if self.running() and shutdown_flag:
            self.logger.info("Stream ended.")
        if not self.running() and shutdown_flag:
            self.logger.info("Task shutdown requested or stream ended. Unclear")
        #self.message_queue.put(self.task_node_id, block=True)
        return self.shutdown()

                    
    def shutdown(self):
        """Shuts down the task.
        """
        
        self.logger.info("Shutting down task")
        self.logger.info("Sent shut down signal to ingest primitive")
        shutdown_future = self.ingest_executor.submit(self.ingest_primitive.close)
        while not shutdown_future.done():
            time.sleep(EdnaDefault.TASK_POLL_TIMEOUT_S)
        self.logger.info("Shut down ingest executor thread")
        self.emit_primitive.flush()
        self.logger.info("Flushed remaining records")
        self.emit_primitive.close()
        self.logger.info("Shut down emit primitive")
        self.logger.info("Shut down ingest primitive")
        self.message_queue.put(self.task_node_id, block=True)
        while self.running():
            time.sleep(EdnaDefault.TASK_POLL_TIMEOUT_S)
        self.ingest_executor.shutdown(wait=False)
        self.logger.info("Finished")
        return True
        
        