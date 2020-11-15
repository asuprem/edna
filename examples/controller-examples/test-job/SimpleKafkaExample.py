from edna.core.execution.context import SimpleStreamingContext
from edna.ingest.streaming import SimulatedIngest
from edna.process.map import JsonToObject, ObjectToJson
from edna.process.filter import KeyedFilter
from edna.emit import KafkaEmit
from edna.serializers import KafkaStringSerializer
from edna.serializers import EmptySerializer

# This file will not work, because it ues only the Base Classes, which was empty.
# You can sue this as a starting point -- replace all the base classes with your needed classes
def filteractorid(actorid):
    return True if actorid>205 else False

def main():

    list_of_inserts = ['{"actor_id":210, "first_name":"jess", "last_name":"st. german", "additional":"unneeded1"}',
            '{"actor_id":201, "first_name":"jess", "last_name":"courtney", "additional":"unneeded2"}', 
            '{"actor_id":202, "first_name":"jess", "last_name":"mishra", "additional":"unneeded3"}', 
            '{"actor_id":203, "first_name":"jess", "last_name":"novinha", "additional":"unneeded4"}',
            '{"actor_id":204, "first_name":"jess", "last_name":"changed", "additional":"unneeded5"}',
            '{"actor_id":205, "first_name":"jess", "last_name":"ael-rayya", "additional":"unneeded6"}', 
            '{"actor_id":206, "first_name":"jess", "last_name":"zuma", "additional":"unneeded7"}', 
            '{"actor_id":207, "first_name":"jess", "last_name":"changed", "additional":"unneeded8"}',
            '{"actor_id":208, "first_name":"jess", "last_name":"changed", "additional":"unneeded9"}',
            '{"actor_id":209, "first_name":"jess", "last_name":"changed", "additional":"unneeded10"}']


    context = SimpleStreamingContext()     # Choose an appropriate context, such as SimpleStreamingContext
    
    ingest_serializer = EmptySerializer()  # e.g. KafkaStringSerializer
    emit_serializer = KafkaStringSerializer()    # e.g. StringSerializer
    
    ingest = SimulatedIngest(serializer=ingest_serializer, stream_list=list_of_inserts)
    p1 = JsonToObject()
    p1 = KeyedFilter(key="actor_id", filter_callable=filteractorid, process=p1)
    p1 = ObjectToJson(process=p1)
    emit = KafkaEmit(emit_serializer, 
        kafka_topic=context.getVariable("export_key"),
        bootstrap_server=context.getVariable("bootstrap_server"),
        emit_buffer_batch_size=1)           # e.g. KafkaEmit


    context.addIngest(ingest=ingest)        # Registers the ingest primitive
    context.addProcess(process=p1)     # Registers the process primitive
    context.addEmit(emit=emit)              # Registers the emit primitive

    context.execute()   # Executes  the context


if __name__ == "__main__":
    main()