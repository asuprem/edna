from edna.serializers import Serializable
from edna.ingest.streaming import BaseStreamingIngest

from typing import Dict
import confluent_kafka, confluent_kafka.admin
from time import sleep
import socket


class KafkaIngest(BaseStreamingIngest):
    """KafkaIngest streams records from a provided kafka topic into the Job. Records are deserialized with the provided serializer.
    """
    def __init__(self, serializer: Serializable, kafka_topic: str,  bootstrap_server: str = "localhost", bootstrap_port: int = 9092, default_group: str ="default-group", *args, **kwargs):
        """Connects to a kafka topic and sets up the ingest

        Args:
            serializer (Serializable): Serializer to convert a message to bytes before sending to kafka.
            kafka_topic (str): Name of kafka topic to publish to.
            bootstrap_server (str, optional): Address of the Kafka bootstrap server. Defaults to "localhost".
            bootstrap_port (int, optional): Bootstrap server port on which the topic is listening for messages. Defaults to 9092.
            default_group (str, optional): Group name for this consumer group. Defaults to "default-group".
        """
        self.kafka_topic = kafka_topic
        conf = {
            "bootstrap.servers": bootstrap_server + ":" + str(bootstrap_port),
            "client.id":socket.gethostname(),
            "group.id":default_group
        }

        self.create_topic(topic_name=kafka_topic, conf=conf)    # TODO is this safe?
        self.consumer = confluent_kafka.Consumer(conf)
        self.consumer.subscribe([self.kafka_topic])
        self.running = True
        super().__init__(serializer=serializer, *args, **kwargs)

    def next(self):
        """Sets up a Kafka Consumer poll to the topic and yields records one by one.

        Raises:
            KafkaException: Propagated from Kafka.

        Returns:
            (obj): A record.
        """
        kafka_message = None
        while kafka_message is None:
            kafka_message = self.consumer.poll(timeout=1.0)
            if kafka_message is None:
                # There is no message to retrieve (methinks)    TODO
                sleep(0.1)
                continue
            if kafka_message.error():
                if kafka_message.error().code() == confluent_kafka.KafkaError._PARTITION_EOF:
                    kafka_message = None
                    pass # TODO will need to add exception handling at some point
                    # End of partition event
                    #sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                    #                    (kafka_message.topic(), kafka_message.partition(), kafka_message.offset()))
                elif kafka_message.error():
                    raise confluent_kafka.KafkaException(kafka_message.error())
        return kafka_message.value()

    def create_topic(self, topic_name: str, conf: Dict):
        """Helper function to create a topic. Blocks until topic is created.

        Args:
            topic_name (str): Topic name to create.
            conf (Dict): Kafka admin client configuration.
        """
        adminclient = confluent_kafka.admin.AdminClient(conf=conf)
        topic = confluent_kafka.admin.NewTopic(topic=topic_name, num_partitions=1)
        response = adminclient.create_topics([topic])
        while not response[topic_name].done():
            sleep(0.1)    # TODO this is super hacky. There is bound to be a better way to do this.
        del adminclient
