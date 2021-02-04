
from os import replace
from edna.core.execution.context import StreamingContext
from edna.api import StreamBuilder
from edna.ingest.streaming import SimulatedIngest

from edna.serializers import EmptySerializer

from edna.process.flatten import StringFlatten
from edna.process.aggregate import RecordCount
from edna.process.map import Map
from edna.emit import StdoutEmit

import logging

import pdb

class AppendString(Map):
    def map(self, record: object) -> object:
        return "Number of words: %i"%record


def main():

    logging.basicConfig(format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG, datefmt="%H:%M:%S")
    
 
    #list_of_inserts = [ 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. At tellus at urna condimentum mattis pellentesque id nibh tortor. Augue eget arcu dictum varius duis at consectetur lorem. Amet porttitor eget dolor morbi non arcu risus quis varius. Non arcu risus quis varius quam quisque id diam vel. Mi quis hendrerit dolor magna eget est lorem ipsum dolor. Orci ac auctor augue mauris augue. Molestie a iaculis at erat pellentesque. Duis at consectetur lorem donec massa sapien faucibus. Viverra nibh cras pulvinar mattis nunc sed blandit libero volutpat. At tempor commodo ullamcorper a lacus vestibulum.',
    #                    'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Mi proin sed libero enim sed faucibus turpis. Dictumst vestibulum rhoncus est pellentesque elit ullamcorper dignissim. Nulla pharetra diam sit amet nisl suscipit adipiscing bibendum est. Facilisi morbi tempus iaculis urna id volutpat lacus laoreet non. Feugiat nibh sed pulvinar proin gravida hendrerit lectus a. Dictum sit amet justo donec. Est velit egestas dui id ornare arcu odio ut. Ornare suspendisse sed nisi lacus sed viverra tellus in. Curabitur gravida arcu ac tortor dignissim convallis aenean et. Enim lobortis scelerisque fermentum dui faucibus.',
    #                    'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Non pulvinar neque laoreet suspendisse. Sociis natoque penatibus et magnis dis parturient montes. Suspendisse faucibus interdum posuere lorem ipsum dolor sit amet consectetur. Sed lectus vestibulum mattis ullamcorper velit sed. Ipsum consequat nisl vel pretium lectus quam. Arcu non sodales neque sodales ut etiam sit. Sodales neque sodales ut etiam sit amet nisl purus in. Aliquam sem et tortor consequat id. Nibh tellus molestie nunc non. Rutrum tellus pellentesque eu tincidunt tortor. Sed cras ornare arcu dui vivamus arcu felis bibendum ut. Nunc aliquet bibendum enim facilisis gravida neque convallis a. Commodo viverra maecenas accumsan lacus vel facilisis. Adipiscing elit duis tristique sollicitudin nibh sit amet commodo. Cras ornare arcu dui vivamus arcu. Cras adipiscing enim eu turpis egestas pretium aenean pharetra magna.']
    #list_of_inserts = ['Hello how are you', 'What is he doing']
    list_of_inserts = ['1 2 3 4', '5 6 7 8']

    context = StreamingContext()
    
    # Ok, so we have a stream     
    stream = StreamBuilder.build(ingest=SimulatedIngest(serializer=EmptySerializer(), stream_list=list_of_inserts), streaming_context=context)
    stream = stream.flatten(flatten_process=StringFlatten(separator=" ")) \
            .aggregate(aggregate_process=RecordCount()) \
            .map(map_process=AppendString()) \
            .emit(emit_process=StdoutEmit(serializer=EmptySerializer()))
            
            #.aggregate(aggregate_process=RecordCount()) \
            #.map(map_process=IntToString()) \
            #.emit(emit_process=StdoutEmit(serializer=EmptySerializer()))
    

    context.addStream(stream=stream)
    context.execute()
    #pdb.set_trace()

if __name__ == "__main__":
    main()