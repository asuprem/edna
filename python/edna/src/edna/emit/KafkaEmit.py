from typing import Dict
from edna.emit import BaseEmit
from edna.serializers import Serializable

from typing import Dict
from time import sleep
import confluent_kafka
import socket
class KafkaEmit(BaseEmit):
    """An Emitter that writes to a Kafka topic."""
    def __init__(self, serializer: Serializable, kafka_topic: str, bootstrap_server: str = "localhost", bootstrap_port: int = 9092):   # For java, need to ensure it is a bytesSerializer
        """Connects to a specified kafka topic and sets up the emitter.

        Args:
            serializer (Serializable): Serializer to convert a message to bytes before sending to kafka.
            kafka_topic (str): Name of kafka topic to publish to.
            bootstrap_server (str, optional): Address of the Kafka bootstrap server. Defaults to "localhost".
            bootstrap_port (int, optional): Bootstrap server port on which the topic is listening for messages. Defaults to 9092.
        """

        self.kafka_topic = kafka_topic
        conf = {
            "bootstrap.servers": bootstrap_server + ":" + str(bootstrap_port),
            "client.id":socket.gethostname()
        }

        self.create_topic(topic_name=kafka_topic, conf=conf)
        
        self.producer = confluent_kafka.Producer(conf)
        super().__init__(serializer=serializer)

    def write(self, message: bytes):
        """Publishes a message to the instance's saved kafka topic.

        Args:
            message (bytes): Serialized byte-encoded message to publish.
        """
        self.producer.produce(self.kafka_topic, value = message)    # Already serialized.

    def create_topic(self, topic_name: str, conf: Dict):
        """Creates a kafka topic using the admin-client api from confluent.

        Args:
            topic_name (str): Name of the topic to create
            conf (Dict): The kafka configuration, containing bootstrap 
            server address and client id
        """
        adminclient = confluent_kafka.admin.AdminClient(conf=conf)
        topic = confluent_kafka.admin.NewTopic(topic=topic_name, num_partitions=1)
        response = adminclient.create_topics([topic])
        while not response[topic_name].done():
            sleep(0.001)    # TODO this is super hacky. There is bound to be a better way to do this.
        del adminclient

