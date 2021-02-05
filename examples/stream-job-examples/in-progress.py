from edna.core.execution.context import StreamingContext
from edna.api import StreamBuilder
from edna.ingest.streaming import SimulatedIngest

from edna.serializers import EmptySerializer

from edna.process.map import JsonToObject
from edna.process.filter import KeyedFilter

from edna.emit import StdoutEmit

import logging




def filteractorid(actorid):
    return True if actorid>205 else False

def filteractorid2(actorid):
    return True if actorid<205 and actorid>202 else False

def main():

    #logging.basicConfig(format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG, datefmt="%H:%M:%S")
    
 
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
    
    # Ok, so we have a stream     
    stream = StreamBuilder.build(ingest=SimulatedIngest(serializer=EmptySerializer(), stream_list=list_of_inserts), streaming_context=context)
    stream = stream.map(map_process=JsonToObject()) \
            .filter(filter_process=KeyedFilter(filter_callable=filteractorid, key="actor_id")) \
            .emit(emit_process=StdoutEmit(serializer=EmptySerializer()))

    stream1 = StreamBuilder.build(ingest=SimulatedIngest(serializer=EmptySerializer(), stream_list=list_of_inserts), streaming_context=context)
    stream1 = stream1.map(map_process=JsonToObject()) \
                    .filter(filter_process=KeyedFilter(filter_callable=filteractorid2, key="actor_id")) \
                    .emit(emit_process=StdoutEmit(serializer=EmptySerializer()))
    

    context.addStream(stream=stream)
    context.addStream(stream=stream1)
    context.execute()
    #pdb.set_trace()

if __name__ == "__main__":
    main()