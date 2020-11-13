from edna.core.execution.context import EdnaContext
from edna.core.configuration import StreamingConfiguration
from edna.types.enums import IngestPattern
import concurrent.futures

from edna.exception import PrimitiveNotSetException

from edna.ingest import BaseIngest
from edna.process import BaseProcess
from edna.emit import BaseEmit


class SimpleStreamingContext(EdnaContext):
    """A `SimpleStreamingContext` is the context for a simple EDNA Job. TODO update this.
    It uses 2 threads - 1 thread for the ingest, and 1 thread for the process and emit.
    It provides methods to control the job execution and to configure job variables.
    See docs for edna.core.execution.context.EdnaContext to initialize

    Attributes:
        ingest (BaseIngest): Stores a reference to an ingest primitive.
        process (BaseProcess): Stores a reference to a process primitive.
        emit (BaseEmit): Stores a reference to an emit primitive

    Args:
        EdnaContext ([Abstract Base Class]): An abstract class for all Contexts that provides the interface for interacting with a Context.
    """        
    ingest: BaseIngest
    process: BaseProcess
    emit: BaseEmit
    def __init__(self, dir : str = ".", confpath : str = "ednaconf.yaml", confclass: StreamingConfiguration = StreamingConfiguration):
        """Initialize the SimpleStreamingContext to accept an EDNA job and configuration.

        Args:
            dir (str, optional): [The directory for the job configuration]. Defaults to the current directory "."
            confpath (str, optional): [A YAML configuration file for the job. Job variables are loaded as top-level 
                fields from this file]. Defaults to "ednaconf.yaml".
            confclass (StreamingConfiguration, optional): [Object to store and interact with the Configuration]. 
                Defaults to edna.core.configuration.StreamingConfiguration.
        """        
        self.ingest_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        super().__init__(dir=dir, confpath=confpath, confclass=confclass)
    
    def addIngest(self, ingest: BaseIngest):
        """Adds the provided ingest primitive to the SimpleStreamingContext

        Args:
            ingest (BaseIngest): Ingest primitive for the SimpleStreamingContext
        """
        self.ingest = ingest
    
    def addProcess(self, process: BaseProcess):
        """Adds the provided process primitive to the SimpleStreamingContext

        Args:
            ingest (BaseProcess): Process primitive for the SimpleStreamingContext
        """
        self.process = process

    def addEmit(self, emit: BaseEmit):
        """Adds the provided emit primitive to the SimpleStreamingContext

        Args:
            ingest (BaseEmit): Emit primitive for the SimpleStreamingContext
        """
        self.emit = emit

    def run(self):  # TODO This should run on a separate thread to handle interrupts
        """This executes the a job for the SimpleStreamingContext. `run` is called through the `execute()` method in the interface.

        Raises:
            NotImplementedError: BUFFERED_INGEST patterns are not implemented in `SimpleStreamingContext`
        """        
        if self.ingest is None:
            raise PrimitiveNotSetException("StreamingContext", "Ingest")
        if self.process is None:
            raise PrimitiveNotSetException("StreamingContext", "Process")
        if self.emit is None:
            raise PrimitiveNotSetException("StreamingContext", "Emit")

        if self.ingest.execution_mode == IngestPattern.STANDARD_INGEST:
            while True:
                record_future = self.ingest_executor.submit(next, self.ingest)
                while not record_future.done():
                    pass    # Perform buffering?
                streaming_record = record_future.result()
                self.emit(self.process(streaming_record)) # Serialization verification TODO
        if self.ingest.execution_mode == IngestPattern.BUFFERED_INGEST:
            raise NotImplementedError

    
            

        
    

