from __future__ import annotations
from typing import Dict
from edna.serializers import Serializable
from edna.ingest import BaseIngest
from edna.serializers import Serializable
from edna.types.enums import IngestPattern
from edna.types.builtin import RecordCollection, StreamRecord, StreamWatermark, StreamShutdown, StreamCheckpoint
from typing import Iterator
import time
from edna.defaults import EdnaDefault

class BaseStreamingIngest(BaseIngest, Iterator):
    """BaseStreamingIngest is the base class for generating records from a streaming source, e.g. Kafka.
    
    Any child class must:

    - Call `super().__init__()` at the end of initialization
    
    - Implement the `next()` method. This should be done as a generator that 
            fetches records in the background and yields them when it is called.
    
    Child classes should NOT:

    - modify the `__call__()` method
    
    - modify the `__iter__()` method

    Attributes:
        execution_mode (IngestPattern): The type of ingest, either STANDARD_INGEST or BUFFERED_INGEST
    """    
    execution_mode = IngestPattern.STANDARD_INGEST
    watermark_timer: float
    checkpoint_timer: float
    shutdown_timer: float
    shutdownWatermark: bool
    shutdownSignal: bool
    def __init__(self,  serializer: Serializable = None, 
                        in_serializer: Serializable = None, 
                        out_serializer: Serializable = None, 
                        logger_name: str = None, 
                        *args, **kwargs):
        """Initialize the primitive with the serializer.

        Args:
            serializer (Serializable): Serializer for deserialize the streaming records.
        """
        if logger_name is None:
            logger_name = self.__class__.__name__
        super().__init__(serializer, in_serializer, out_serializer, logger_name, *args, **kwargs)
        self.shutdown_timer = kwargs.get("shutdown_timer", None) if kwargs.get("shutdown_timer", None) is not None else float('inf')
        self.logger.debug("Set shutdown timer to %s"%str(self.shutdown_timer))
        self.watermark_timer = kwargs.get("watermark_timer", None) if kwargs.get("watermark_timer", None) is not None else float('inf')
        self.logger.debug("Set watermark timer to %s"%str(self.shutdown_timer))
        self.checkpoint_timer = kwargs.get("checkpoint_timer", None) if kwargs.get("checkpoint_timer", None) is not None else float('inf')
        self.logger.debug("Set checkpoint timer to %s"%str(self.shutdown_timer))
        self.shutdownWatermark = False
        self.shutdownSignal = False
    
    def __iter__(self):
        """Returns itself as the iterator.

        Returns:
            (Iterator) : The class as an iterator.
        """
        return self

    def __next__(self) -> RecordCollection[StreamRecord]:
        """Fetches the next record from the source and deserializes

        Returns:
            (RecordCollection[StreamRecord]): Single fetched record in a singleton format.
        """

        if self.shutdownWatermark:
            return self.waitForShutdown()
        if self.shutdownSignal:
            return self.shutdownSignalReceived()
        
        if self.hasNext():
            return_record = RecordCollection(
                [
                    StreamRecord(self.in_serializer.read(self.next()))
                    ]
            )
            
        else:
            self.logger.debug("Stream has ended. Release shutdown.")
            self.shutdownWatermark = True
            return_record = RecordCollection(
                [
                    StreamShutdown()
                    ]
            )
        ctime = time.time()
        if self.checkWatermarkRecord(ctime):
            self.logger.debug("Release watermark")
            return_record += [StreamWatermark()]
        if self.checkCheckpointRecord(ctime):
            self.logger.debug("Release checkpoint")
            return_record += [StreamCheckpoint()]
        if not self.shutdownWatermark and self.checkShutdownRecord(ctime):  # makes sure we haven't already shut down the stream
            self.logger.debug("Release shutdown")
            return_record += [StreamShutdown()]
        return return_record

    def hasNext(self) -> bool:
        return True

    def next(self) -> object:
        """Method that encapsulates raw record fetching logic.

        Raises:
            NotImplementedError: Child classes should implement this method.
        """
        raise NotImplementedError

    def build(self, build_configuration: Dict[str,str]):
        """Lazy building for ingest.
        """
        self.logger.debug("Building ingest")
        self.shutdown_time = time.time()
        self.checkpoint_time = time.time()
        self.watermark_time = time.time()
        self.buildIngest(build_configuration)
        self.logger.debug("Completed building ingest")

    def buildIngest(self, build_configuration: Dict[str,str]):
        """Should be implemented by subclasses

        Args:
            build_configuration (Dict[str,str]): The build configuration
        """
        pass

    def shutdownIngest(self):
        """Should be implemented by subclasses
        """
        pass

    def waitForShutdown(self):
        self.logger.debug("Waiting for shut down signal")
        while not self.shutdownSignal:
            time.sleep(EdnaDefault.POLL_TIMEOUT_S)
        self.logger.debug("Waiting for shut down signal -- signal received")
        return self.shutdownSignalReceived()

    def shutdownSignalReceived(self):
        self.logger.debug("Received shut down signal")
        self.shutdownIngest()
        self.logger.debug("Finished shutting down Ingest")
        return None


    def close(self):
        """Shuts down the ingest, closing any connections if they exist
        """
        self.logger.debug("Triggered shut down signal")
        self.shutdownSignal = True

    def checkShutdownRecord(self, ctime):
        if ctime - self.shutdown_time > self.shutdown_timer:
            self.shutdownWatermark = True
        return self.shutdownWatermark
    
    def checkCheckpointRecord(self, ctime):
        if ctime - self.checkpoint_time > self.checkpoint_timer:
            self.checkpoint_time = ctime
            return True
        return False
    
    def checkWatermarkRecord(self, ctime):
        if ctime - self.watermark_time > self.watermark_timer:
            self.watermark_time = ctime
            return True
        return False

from .TwitterStreamingIngest import TwitterStreamingIngest
from .TwitterFilteredIngest import TwitterFilteredIngest
from .KafkaIngest import KafkaIngest
from .SimulatedIngest import SimulatedIngest

__pdoc__ = {}
__pdoc__["BaseStreamingIngest.__iter__"] = True
__pdoc__["BaseStreamingIngest.__next__"] = True