
import logging
from edna.core.execution.context import StreamingContext
from edna.api import StreamBuilder

from edna.ingest.streaming import SimulatedIngest
from edna.process.map import JsonToObject, ObjectToSQL
from edna.core.factories import SQLTupleFactory
from edna.emit import SQLUpsertEmit

from edna.serializers import EmptySerializer

def main():

    logging.basicConfig(format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',level=logging.INFO, datefmt="%H:%M:%S")


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
    tuple_factory = SQLTupleFactory(tuple_fields=context.getVariable("sql_fields"), upsert_fields=context.getVariable("upsert_fields")) 
    
    stream = StreamBuilder.build(
        SimulatedIngest(
            stream_list=list_of_inserts)
    ).map(
        JsonToObject()
    ).map(
        ObjectToSQL(tuple_factory=tuple_factory)
    ).emit(
        SQLEmit(
            database=context.getVariable("database"), 
            host=context.getVariable("host"), 
            user=context.getVariable("user"), 
            password=context.getVariable("password"),
            table=context.getVariable("table"),
            tuple_factory=tuple_factory)
    )
    
    context.addStream(stream)

    context.execute()

if __name__ == "__main__":
    main()