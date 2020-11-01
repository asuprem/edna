from edna.core.execution.context import EdnaContext
from edna.ingest import BaseIngest
from edna.process import BaseProcess
from edna.emit import BaseEmit
from edna.serializers import Serializable

# This file will not work, because it uses only the Base Classes, which was empty.
# You can use  this as a starting point -- replace all the base classes with your needed classes

def main():
    context = EdnaContext()     # Choose an appropriate context, such as SimpleStreamingContext
    
    ingest_serializer = Serializable()  # e.g. KafkaStringSerializer
    emit_serializer = Serializable()    # e.g. StringSerializer
    
    ingest = BaseIngest(ingest_serializer, context.getVariable("VARIABLE1"))    # e.g. KafkaIngest
    process = BaseProcess(context.getVariable("VARIABLE2"))                     # e.g. BaseProcess
    emit = BaseEmit(emit_serializer, context.getVariable("VARIABLE1"))          # e.g. KafkaEmit

    context.addIngest(ingest=ingest)        # Registers the ingest primitive
    context.addProcess(process=process)     # Registers the process primitive
    context.addEmit(emit=emit)              # Registers the emit primitive

    context.execute()   # Executes  the context


if __name__ == "__main__":
    main()