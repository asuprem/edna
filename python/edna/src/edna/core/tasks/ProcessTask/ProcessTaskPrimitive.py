from __future__ import annotations

from edna.buffer import ByteBuffer
from edna.process import BaseProcess
from edna.defaults import EdnaDefault
from edna.core.tasks import BufferedTaskPrimitive

import socket




class ProcessTaskPrimitive(BufferedTaskPrimitive):
    buffer: ByteBuffer
    sender: socket.socket
    receiver: socket.socket
    primitive: BaseProcess
    def __init__(self, process_primitive: BaseProcess,
            ingest_port : int,
            emit_port : int, 
            max_buffer_size : int = EdnaDefault.BUFFER_MAX_SIZE, 
            max_buffer_timeout : float = EdnaDefault.BUFFER_MAX_TIMEOUT_S):

        super().__init__(max_buffer_size=max_buffer_size, max_buffer_timeout=max_buffer_timeout)
        self.ingest_port = ingest_port
        self.emit_port = emit_port
        self.primitive = process_primitive
        self.ip = EdnaDefault.TASK_PRIMITIVE_HOST

        self.sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sender.connect((self.ip, self.emit_port))
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receiver.bind((self.ip, self.ingest_port))
        self.receiver.listen(1)

        

    def run(self):
        client, _ = self.receiver.accept()
        while self.running():
            try:
                client.settimeout(self.MAX_BUFFER_TIMEOUT_S)
                message = client.recv(self.MAX_BUFFER_SIZE)
                self.primitive.in_serializer.feed(message)
            except socket.timeout as e:
                # We check if the buffers have timed out.
                self.checkBufferTimeout()

            # Now we have a buunch of buffered messages in the out_serializer. We will process them all 
            # immediately and write them to the output buffer.
            for record in self.primitive.in_serializer:
                completed_records = self.primitive([record])
                for processed_record in completed_records:  # Completed records are lists
                    # TODO possible this with nogil???
                    self.buffer.write(self.primitive.out_serializer.write(processed_record))
                    self.checkBufferTimeout()
                self.checkBufferTimeout()

        self.shutdown()

    def shutdown(self):
        self.receiver.close()
        self.sender.close()