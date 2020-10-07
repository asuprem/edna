from edna.core.execution.context import StreamingContext

from edna.ingest.streaming import SimulatedIngest
from edna.process.map import JsonToObject, ObjectToSQL
from edna.core.factories import SQLTupleFactory
from edna.emit import SQLEmit

from edna.serializers.EmptySerializer import EmptyStringSerializer
from edna.serializers.EmptySerializer import EmptyObjectSerializer

def main():

    list_of_inserts = ['{"first_name":"jessica", "last_name":"st. german", "additional":"unneeded1"}',
            '{"first_name":"jessica", "last_name":"courtney", "additional":"unneeded2"}', 
            '{"first_name":"jessica", "last_name":"mishra", "additional":"unneeded3"}', 
            '{"first_name":"jessica", "last_name":"novinha", "additional":"unneeded4"}',
            '{"first_name":"jessica", "last_name":"tudor", "additional":"unneeded5"}',
            '{"first_name":"jessica", "last_name":"ael-rayya", "additional":"unneeded6"}', 
            '{"first_name":"jessica", "last_name":"zuma", "additional":"unneeded7"}', 
            '{"first_name":"jessica", "last_name":"akihita", "additional":"unneeded8"}',
            '{"first_name":"jessica", "last_name":"xi", "additional":"unneeded9"}',
            '{"first_name":"jessica", "last_name":"kurylova", "additional":"unneeded10"}']

    context = StreamingContext()
    tuple_factory = SQLTupleFactory(tuple_fields=context.getVariable("sql_fields")) 

    ingest = SimulatedIngest(serializer=EmptyStringSerializer, stream_list=list_of_inserts)
    process = ObjectToSQL(process=JsonToObject(), tuple_factory=tuple_factory)
    emit = SQLEmit(serializer=EmptyObjectSerializer, 
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