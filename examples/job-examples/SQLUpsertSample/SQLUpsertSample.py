from edna.core.execution.context import StreamingContext

from edna.ingest.streaming import SimulatedIngest
from edna.process.map import JsonToObject, ObjectToSQL
from edna.core.factories import SQLTupleFactory
from edna.emit import SQLUpsertEmit

from edna.serializers.EmptySerializer import EmptyStringSerializer
from edna.serializers.EmptySerializer import EmptyObjectSerializer

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

    context = StreamingContext()
    tuple_factory = SQLTupleFactory(tuple_fields=context.getVariable("sql_fields"), upsert_fields=context.getVariable("upsert_fields")) 

    ingest = SimulatedIngest(serializer=EmptyStringSerializer, stream_list=list_of_inserts)
    process = ObjectToSQL(process=JsonToObject(), tuple_factory=tuple_factory)
    emit = SQLUpsertEmit(serializer=EmptyObjectSerializer, 
        database=context.getVariable("database"), 
        host=context.getVariable("host"), 
        user=context.getVariable("user"), 
        password=context.getVariable("password"),
        table=context.getVariable("table"),
        tuple_factory=tuple_factory)

    context.addIngest(ingest=ingest)
    context.addProcess(process=process)
    context.addEmit(emit=emit)

    context.execute()

if __name__ == "__main__":
    main()