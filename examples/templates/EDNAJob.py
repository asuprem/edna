import logging
from edna.core.execution.context import StreamingContext
from edna.api import StreamBuilder

# Import the necessary processes
from edna.ingest import BaseIngest
from edna.process import BaseProcess
from edna.emit import BaseEmit

# Import the necessary serializers and deserializers
from edna.serializers import Serializable

# This file will not work, because it uses only the Base Classes, which are empty.
# You can use  this as a starting point -- replace all the base classes with your needed classes

def main():
    # Set up logging
    # You can comment out this line if you want. You can change the logging level to DEBUG or any
    #    other logging level as needed.
    logging.basicConfig(format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',level=logging.INFO, datefmt="%H:%M:%S")

    # Set up the context
    context = StreamingContext()
    
    # Set up the serializers. This might not be needed if you don't need to serialize or deserialize the 
    # inputs and outputs
    ingest_serializer = Serializable()  # e.g. KafkaStringSerializer
    emit_serializer = Serializable()    # e.g. StringSerializer
    

    # Build a stream
    stream = StreamBuilder.build(
            ingest=BaseIngest(
                serializer=ingest_serializer
                ), 
            streaming_context=context
        ).map(
            map_process=BaseProcess()
        ).filter(
            filter_process=BaseProcess()
        ).flatten(
            flatten_process=BaseProcess()
        ).map(
            map_process=BaseProcess()
        ).emit(
            emit_process=BaseEmit(
                serializer=emit_serializer
                )
        )

    # Add the stream to the context
    context.addStream(stream=stream)

    # Execute the context
    context.execute()


if __name__ == "__main__":
    main()