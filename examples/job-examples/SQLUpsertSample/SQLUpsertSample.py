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
    
    stream = StreamBuilder.build(
        SimulatedIngest(
            stream_list=list_of_inserts)
    ).map(
        JsonToObject()
    ).map(
        ObjectToSQL(tuple_factory=tuple_factory)
    ).emit(
        SQLUpsertEmit(
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