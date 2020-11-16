import logging
from edna.core.execution.context import StreamingContext
from edna.api import StreamBuilder

from edna.ingest.streaming import KafkaIngest
from edna.emit import KafkaEmit
from edna.serializers import KafkaStringSerializer
from edna.serializers import StringSerializer


def main():
    logging.basicConfig(format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',level=logging.INFO, datefmt="%H:%M:%S")
    context = StreamingContext()     # Choose an appropriate context, such as SimpleStreamingContext
    
    ingest_serializer = KafkaStringSerializer()
    emit_serializer = StringSerializer()
    

    stream = StreamBuilder.build(
        ingest=KafkaIngest(
            ingest_serializer, 
            kafka_topic=context.getVariable("import_key"),
            bootstrap_server=context.getVariable("bootstrap_server"))
    ).emit(
        KafkaEmit(
            emit_serializer, 
            kafka_topic=context.getVariable("export_key"),
            bootstrap_server=context.getVariable("bootstrap_server"))
    )
    
    context.addStream(stream)

    context.execute()   # Executes  the context


if __name__ == "__main__":
    main()
