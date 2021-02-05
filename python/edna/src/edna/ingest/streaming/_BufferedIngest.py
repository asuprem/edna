from __future__ import annotations
from edna.defaults import EdnaDefault
from edna.serializers import MsgPackBufferedSerializer
from edna.types.enums import IngestPattern, StreamElementType
from edna.ingest.streaming import BaseStreamingIngest
from edna.types.builtin import RecordCollection, StreamElement, StreamCheckpoint, StreamRecord, StreamWatermark, StreamShutdown
from typing import Dict, Tuple
import socket

class _BufferedIngest(BaseStreamingIngest):
    """This ingest yields record from a network buffer, usually written to by a
    `edna.emit._BufferedEmit`.
    """
    def __init__(self, receive_from_node_id: int, serializer: MsgPackBufferedSerializer = MsgPackBufferedSerializer(),  *args, **kwargs):
        """Initializes the ingest

        Args:
            serializer (MsgPackBufferedSerializer): The deserializer for this ingest
            receive_from_node_id (int): The source PhysicalGraphNode in the current StreamingContext's
                PhysicalGraph node that emits to this ingest.
        """
        super().__init__(serializer=serializer, 
            logger_name = self.__class__.__name__,
            *args, **kwargs)
        self.receive_from_node_id = receive_from_node_id
        self.execution_mode = IngestPattern.BUFFERED_INGEST
        self.running = False
        self.client = None
        self.receiver = None
        self.MAX_BUFFER_TIMEOUT_S = EdnaDefault.BUFFER_MAX_TIMEOUT_S
        self.MAX_BUFFER_SIZE = EdnaDefault.BUFFER_MAX_SIZE

    def getSourceNodeId(self) -> int:
        """Gets the id of the source PhysicalGraphNode that emits to this ingest

        Returns:
            int: The node id of the source PhysicalGraphNode
        """
        return self.receive_from_node_id


    def __next__(self) -> RecordCollection[StreamElement]:
        """Fetches the next record from the source and deserializes

        Returns:
            (RecordCollection[StreamRecord]): Single fetched record in a singleton format.
        """

        if self.shutdownWatermark:
            return self.waitForShutdown()
        if self.shutdownSignal:
            return self.shutdownSignalReceived()
        
        stream_record = self.next()
        if stream_record[0] == 2:
            stream_record = StreamCheckpoint()
        elif stream_record[0] == 1:
            stream_record = StreamRecord(stream_record[1])
        elif stream_record[0] == 4:
            stream_record = StreamShutdown()
        elif stream_record[0] == 3:
            stream_record = StreamWatermark()
        else:
            raise RuntimeError("Invalid Stream Element type")
        return_record = RecordCollection(
            [
                stream_record
                ]
        )
        if stream_record.isShutdown():
            self.logger.debug("Received shutdown watermark for BufferedIngest. Setting flags.")
            self.shutdownWatermark = True
        #print("Ingested at bufferedingest -->", (type(stream_record.getValue()), stream_record.getValue()))
        self.logger.debug("Build buffer record --> %s", str((return_record[0].elementType, return_record[0].getValue())))
        return return_record

    def next(self) -> Tuple[int,object]:
        """Yields a record from the source.

        Returns:
            object: A record.
        """
        record = None
        while record is None:
            try:    # Check if we still have records to process
                record = self.serializer.next()
                self.logger.debug("IngestBuffer -- raw buffer record (%s)  %s"%(str(self.serializer), str(record)))
            except StopIteration:
                # No more records to process
                try:    # Get new records
                    self.client.settimeout(self.MAX_BUFFER_TIMEOUT_S)   # TODO pass them from task primitive...
                    serialized_record = self.client.recv(self.MAX_BUFFER_SIZE)
                    if len(serialized_record):
                        self.serializer.feed(serialized_record)   # Send to the MsgPackBufferedSerializer...
                        self.logger.debug("Received new records from socket (%s):  %s"%(str(self.serializer), str(serialized_record)))
                except socket.timeout as e: # No records received
                    #self.logger.debug("Socket timed out")
                    pass
        self.logger.debug("IngestBuffer -- raw buffer record (2)   %s", str(record))
        return record
                
                
    def buildIngest(self, build_configuration: Dict[str,str]):
        """Builds the network buffer receiver.

        Args:
            build_configuration (Dict[str,str]): Contains required attributes for the receiver, 
                such as `max_buffer_size`, `max_buffer_timeout`, `ingest_port`, and host `ip`
        """
        self.MAX_BUFFER_SIZE = build_configuration["max_buffer_size"]
        self.MAX_BUFFER_TIMEOUT_S = build_configuration["max_buffer_timeout"]
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.receiver.bind((build_configuration["ip"], build_configuration["ingest_port"]))
        self.receiver.bind(('', build_configuration["ingest_port"]))
        self.receiver.listen(1)
        self.logger.debug("Completed building BufferedIngest listening on port %i"%build_configuration["ingest_port"])
        self.client, _ = self.receiver.accept()


    def shutdownIngest(self):
        """Shuts down the ingest, closing any connections if needed.
        """
        self.receiver.close()