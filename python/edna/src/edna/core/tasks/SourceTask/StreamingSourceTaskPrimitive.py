from __future__ import annotations

from edna.buffer import ByteBuffer
from edna.defaults import EdnaDefault
from edna.core.tasks import BufferedTaskPrimitive
from edna.ingest.streaming import BaseStreamingIngest
from edna.types.enums.IngestPattern import IngestPattern

import concurrent.futures
import socket
import time


class StreamingSourceTaskPrimitive(BufferedTaskPrimitive):
    buffer: ByteBuffer
    sender: socket.socket
    primitive: BaseStreamingIngest
    def __init__(self, ingest_primitive: BaseStreamingIngest,
            emit_port : int, 
            max_buffer_size : int = EdnaDefault.BUFFER_MAX_SIZE, 
            max_buffer_timeout : float = EdnaDefault.BUFFER_MAX_TIMEOUT_S):

        super().__init__(max_buffer_size=max_buffer_size, max_buffer_timeout=max_buffer_timeout)
        self.port = emit_port
        self.primitive = ingest_primitive
        self.ip = EdnaDefault.TASK_PRIMITIVE_HOST
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sender.connect((self.ip, self.port))
        
        self.ingest_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        #packer = msgpack.Packer()
        #self.serialize = packer.pack
        

    def run(self):
        # Okay, so basically, we will have a wrapper loop that checks timeout and flushes the buffer, then polls the ingest primitive...
        record_future = None
        if self.ingest.execution_mode == IngestPattern.CLIENT_SIDE_STREAM:
            while self.running(): # loop
                if record_future is None:   # Not set
                    record_future = self.ingest_executor.submit(next, self.primitive)
                if record_future.done():
                    streaming_records = record_future.result()
                    for record in streaming_records:    # Because ingest returns a List (usually singleton)
                        self.buffer.write(self.ingest.out_serializer.write(record))
                    record_future = None
                self.checkBufferTimeout()
        else:
            raise NotImplementedError
        self.shutdown()

    def shutdown(self):
        self.sender.close()
        # TODO --> saving to disk with a checkpoint??