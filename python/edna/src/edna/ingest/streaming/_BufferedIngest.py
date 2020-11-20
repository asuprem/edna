from edna.defaults import EdnaDefault
from edna.serializers import MsgPackBufferedSerializer
from edna.types.enums import IngestPattern
from edna.serializers import Serializable
from edna.ingest.streaming import BaseStreamingIngest

from typing import Dict
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

    def next(self) -> object:
        """Yields a record from the source.

        Returns:
            object: A record.
        """
        record = None
        while record is None:
            try:    # Check if we still have records to process
                record = self.serializer.next()
            except StopIteration:
                # No more records to process
                try:    # Get new records
                    self.client.settimeout(self.MAX_BUFFER_TIMEOUT_S)   # TODO pass them from task primitive...
                    serialized_record = self.client.recv(self.MAX_BUFFER_SIZE)
                    self.serializer.feed(serialized_record)   # Send to the MsgPackBufferedSerializer...
                except socket.timeout as e: # No records received
                    pass
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
        self.client, _ = self.receiver.accept()


    def shutdownIngest(self):
        """Shuts down the ingest, closing any connections if needed.
        """
        self.receiver.close()