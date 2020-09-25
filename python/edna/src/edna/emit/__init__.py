from edna.serializers import Serializable

class BaseEmit(object):
    """BaseEmit is the base class for writing records from an edna.process to a sink, 
    such as a filestream, sql database, or Kafka topic.

    Any edna.emit function inherits from BaseEmit and must implement the write() function.
    """  
    def __init__(self, serializer: Serializable):
        self.serializer = serializer

    def __call__(self, message):
        self.write(self.serializer.write(message))

    def write(self,message):        # For Java, need Emit to be a templated function for message type
        raise NotImplementedError()

from .KafkaEmit import KafkaEmit
from .StdoutEmit import StdoutEmit




