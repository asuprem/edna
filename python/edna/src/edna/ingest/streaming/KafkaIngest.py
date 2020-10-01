from edna.serializers import Serializable
from edna.ingest.streaming import BaseStreamingIngest

from typing import Dict
from confluent_kafka import Consumer, admin, KafkaError, KafkaException
from time import sleep
import socket


class KafkaIngest(BaseStreamingIngest):
    def __init__(self, serializer: Serializable, kafka_topic: str,  bootstrap_server: str = "localhost", bootstrap_port: int = 9092, default_group: str ="default-group"):
        self.kafka_topic = kafka_topic
        conf = {
            "bootstrap.servers": bootstrap_server + ":" + str(bootstrap_port),
            "client.id":socket.gethostname(),
            "group.id":default_group
        }

        self.create_topic(topic_name=kafka_topic, conf=conf)    # TODO is this safe?
        self.consumer = Consumer(conf)
        self.consumer.subscribe([self.kafka_topic])
        self.running = True
        super().__init__(serializer=serializer)

    def next(self):
        kafka_message = None
        while kafka_message is None:
            kafka_message = self.consumer.poll(timeout=1.0)
            if kafka_message.error():
                if kafka_message.error().code() == KafkaError._PARTITION_EOF:
                    kafka_message = None
                    pass # TODO will need to add exception handling at some point
                    # End of partition event
                    #sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                    #                    (kafka_message.topic(), kafka_message.partition(), kafka_message.offset()))
                elif kafka_message.error():
                    raise KafkaException(kafka_message.error())
        return kafka_message

    def create_topic(self, topic_name: str, conf: Dict):
        adminclient = admin.AdminClient(conf=conf)
        topic = admin.NewTopic(topic=topic_name, num_partitions=1)
        response = adminclient.create_topics([topic])
        while not response[topic_name].done():
            sleep(0.001)    # TODO this is super hacky. There is bound to be a better way to do this.
        del adminclient
