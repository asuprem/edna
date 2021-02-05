from edna.core.execution.context import StreamingContext
from edna.api import StreamBuilder
from edna.ingest.streaming import SimulatedIngest

from edna.serializers import EmptySerializer

from edna.emit import StdoutEmit

import logging
import ctypes

def main():

    logging.basicConfig(format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG, datefmt="%H:%M:%S")
    
    #libgcc_s = ctypes.CDLL('libgcc_s.so.1')

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
    
    #list_of_inserts = ['{"actor_id":210, "first_name":"jess", "last_name":"st. german", "additional":"unneeded1"}']

    context = StreamingContext()
    # Ok, so we have a stream     
    stream = StreamBuilder.build(ingest=SimulatedIngest(serializer=EmptySerializer(), stream_list=list_of_inserts), streaming_context=context)
    stream = stream.emit(StdoutEmit(serializer=EmptySerializer()))
    
    context.addStream(stream=stream)
    context.execute()


if __name__ == "__main__":
    main()