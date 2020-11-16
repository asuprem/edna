import logging
from edna.api import StreamBuilder
from edna.core.execution.context import StreamingContext
from edna.serializers import KafkaStringSerializer
from edna.ingest.streaming import KafkaIngest
from edna.process import BaseProcess
from edna.emit import KafkaEmit


def main():
    logging.basicConfig(format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',level=logging.INFO, datefmt="%H:%M:%S")
    context = StreamingContext()

    stream = StreamBuilder.build(
        KafkaIngest(
            serializer=KafkaStringSerializer(), 
            kafka_topic=context.getVariable("import_key"),
            bootstrap_server=context.getVariable("bootstrap_server"), 
            bootstrap_port=context.getVariable("bootstrap_port"))
    ).emit(
        KafkaEmit(
            serializer=KafkaStringSerializer(), 
            kafka_topic=context.getVariable("export_key"),
            bootstrap_server=context.getVariable("bootstrap_server"),
            bootstrap_port=context.getVariable("bootstrap_port"))
    )

    context.addStream(stream)
    context.execute()


if __name__ == "__main__":
    main()