from edna.serializers import Serializable
from edna.ingest.streaming import BaseStreamingIngest

from typing import Dict
import confluent_kafka, confluent_kafka.admin
from time import sleep
import socket


class KafkaIngest(BaseStreamingIngest):
    """KafkaIngest streams records from a provided kafka topic into the Job. Records are deserialized with the provided serializer.
    """
    def __init__(self, kafka_topic: str,  bootstrap_server: str = "localhost", bootstrap_port: int = 9092, default_group: str ="default-group", serializer: Serializable = None, *args, **kwargs):
        """Connects to a kafka topic and sets up the ingest

        Args:
            serializer (Serializable): Serializer to convert a record to bytes before sending to kafka.
            kafka_topic (str): Name of kafka topic to publish to.
            bootstrap_server (str, optional): Address of the Kafka bootstrap server. Defaults to "localhost".
            bootstrap_port (int, optional): Bootstrap server port on which the topic is listening for records. Defaults to 9092.
            default_group (str, optional): Group name for this consumer group. Defaults to "default-group".
        """
        super().__init__(serializer=serializer, *args, **kwargs)
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
        

    def next(self):
        """Sets up a Kafka Consumer poll to the topic and yields records one by one.

        Raises:
            KafkaException: Propagated from Kafka.

        Returns:
            (obj): A record.
        """
        kafka_record = None
        while kafka_record is None:
            kafka_record = self.consumer.poll(timeout=1.0)
            if kafka_record is None:
                # There is no record to retrieve (methinks)    TODO
                sleep(0.1)
                continue
            if kafka_record.error():
                if kafka_record.error().code() == confluent_kafka.KafkaError._PARTITION_EOF:
                    kafka_record = None
                    pass # TODO will need to add exception handling at some point
                    # End of partition event
                    #sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                    #                    (kafka_record.topic(), kafka_record.partition(), kafka_record.offset()))
                elif kafka_record.error():
                    raise confluent_kafka.KafkaException(kafka_record.error())
        return kafka_record.value()

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
