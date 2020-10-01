from typing import Dict
from edna.emit import BaseEmit
from edna.serializers import Serializable

from typing import Dict
from time import sleep
from confluent_kafka import Producer, admin
import socket
class KafkaEmit(BaseEmit):
    """An Emitter that writes to a Kafka topic"""
    def __init__(self, serializer: Serializable, kafka_topic: str, bootstrap_server: str = "localhost", bootstrap_port: int = 9092):   # For java, need to ensure it is a bytesSerializer

        self.kafka_topic = kafka_topic
        conf = {
            "bootstrap.servers": bootstrap_server + ":" + str(bootstrap_port),
            "client.id":socket.gethostname()
        }

        self.create_topic(topic_name=kafka_topic, conf=conf)
        
        self.producer = Producer(conf)
        super().__init__(serializer=serializer)

    def write(self, message: bytes):
        self.producer.produce(self.kafka_topic, value = message)    # Already serialized.

    def create_topic(self, topic_name: str, conf: Dict):
        adminclient = admin.AdminClient(conf=conf)
        topic = admin.NewTopic(topic=topic_name, num_partitions=1)
        response = adminclient.create_topics([topic])
        while not response[topic_name].done():
            sleep(0.001)    # TODO this is super hacky. There is bound to be a better way to do this.
        del adminclient
            