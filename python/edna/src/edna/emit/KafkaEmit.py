from edna.emit import BaseEmit
from edna.serializers import Serializable

from confluent_kafka import Producer
import socket
class KafkaEmit(BaseEmit):
    """An Emitter that writes to a Kafka topic"""
    def __init__(self, serializer: Serializable, kafka_topic: str, bootstrap_server: str = None):   # For java, need to ensure it is a bytesSerializer

        self.kafka_topic = kafka_topic
        conf = {
            "bootstrap.servers": bootstrap_server if bootstrap_server is not None else "localhost",
            "client.id":socket.gethostname()
        }
        self.producer = Producer(conf)
        super().__init__(serializer=serializer)

    def write(self, message: bytes):
        self.producer.produce(self.kafka_topic, value = message)

        