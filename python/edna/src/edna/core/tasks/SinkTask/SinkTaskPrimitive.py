from __future__ import annotations
from python.edna.src.edna import emit

from edna.emit import BaseEmit
from edna.defaults import EdnaDefault
from edna.core.tasks import TaskPrimitive

import socket




class SinkTaskPrimitive(TaskPrimitive):
    receiver: socket.socket
    def __init__(self, emit_primitive: BaseEmit,
            ingest_port: int,
            max_buffer_size = EdnaDefault.BUFFER_MAX_SIZE, 
            max_buffer_timeout = EdnaDefault.BUFFER_MAX_TIMEOUT_S):
        super().__init__(max_buffer_size=max_buffer_size, max_buffer_timeout=max_buffer_timeout)
        
        self.port = ingest_port
        self.primitive = emit_primitive
        self.ip = EdnaDefault.TASK_PRIMITIVE_HOST

        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receiver.bind((self.ip, self.port))
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
                pass

            for record in self.primitive.in_serializer:
                self.primitive([record])
        
        self.shutdown()

    def shutdown(self):
        self.receiver.close()

        
        
    