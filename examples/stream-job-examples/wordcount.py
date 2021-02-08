#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Context
from edna.core.execution.context import StreamingContext

# Serializers
from edna.serializers import EmptySerializer

# Ingest primitives and builder
from edna.api import StreamBuilder
from edna.ingest.streaming import SimulatedIngest

# Process primitives
from edna.process.flatten import StringFlatten
from edna.process.aggregate import RecordCount
from edna.process.map import Map

# Emit primitives
from edna.emit import StdoutEmit

# Logging
import logging


# A custom Map operator
class AppendString(Map):
    """AppendString is a custom Map operator. It takes in a record that denotes the number of words in the current stream window, 
    and emits a string `Number of words: (#)`, where `(#)` is the number of words argument.

    Args:
        Map (BaseProcess): The superclass for AppendString
    """
    def map(self, record: object) -> object:
        """Appends (technically prepends) the string `Number of words` to the number of words in the stream.

        Args:
            record (object): The number of records so far.

        Returns:
            object: A string.
        """
        return "Number of words: %s"%record

def main():
    # Set up logging. Change level to DEBUG if desired 
    logging.basicConfig(format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',level=logging.INFO, datefmt="%H:%M:%S")
    
    # Some sample finite streams
    list_of_inserts = [ 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. At tellus at urna condimentum mattis pellentesque id nibh tortor. Augue eget arcu dictum varius duis at consectetur lorem. Amet porttitor eget dolor morbi non arcu risus quis varius. Non arcu risus quis varius quam quisque id diam vel. Mi quis hendrerit dolor magna eget est lorem ipsum dolor. Orci ac auctor augue mauris augue. Molestie a iaculis at erat pellentesque. Duis at consectetur lorem donec massa sapien faucibus. Viverra nibh cras pulvinar mattis nunc sed blandit libero volutpat. At tempor commodo ullamcorper a lacus vestibulum.',
                        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Mi proin sed libero enim sed faucibus turpis. Dictumst vestibulum rhoncus est pellentesque elit ullamcorper dignissim. Nulla pharetra diam sit amet nisl suscipit adipiscing bibendum est. Facilisi morbi tempus iaculis urna id volutpat lacus laoreet non. Feugiat nibh sed pulvinar proin gravida hendrerit lectus a. Dictum sit amet justo donec. Est velit egestas dui id ornare arcu odio ut. Ornare suspendisse sed nisi lacus sed viverra tellus in. Curabitur gravida arcu ac tortor dignissim convallis aenean et. Enim lobortis scelerisque fermentum dui faucibus.',
                        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Non pulvinar neque laoreet suspendisse. Sociis natoque penatibus et magnis dis parturient montes. Suspendisse faucibus interdum posuere lorem ipsum dolor sit amet consectetur. Sed lectus vestibulum mattis ullamcorper velit sed. Ipsum consequat nisl vel pretium lectus quam. Arcu non sodales neque sodales ut etiam sit. Sodales neque sodales ut etiam sit amet nisl purus in. Aliquam sem et tortor consequat id. Nibh tellus molestie nunc non. Rutrum tellus pellentesque eu tincidunt tortor. Sed cras ornare arcu dui vivamus arcu felis bibendum ut. Nunc aliquet bibendum enim facilisis gravida neque convallis a. Commodo viverra maecenas accumsan lacus vel facilisis. Adipiscing elit duis tristique sollicitudin nibh sit amet commodo. Cras ornare arcu dui vivamus arcu. Cras adipiscing enim eu turpis egestas pretium aenean pharetra magna.']
    #list_of_inserts = ['Hello how are you', 'What is he doing']
    #list_of_inserts = ['9 8 7 6', '5 4']

    # Set up the StreamingContext
    context = StreamingContext()
    
    # Build the ingest 
    stream = StreamBuilder.build(
                ingest=SimulatedIngest(
                    serializer=EmptySerializer(), 
                    stream_list=list_of_inserts), 
                streaming_context=context)
    # Setup the process(es) and emit
    stream = stream.flatten(flatten_process=StringFlatten(separator=" ")) \
                .aggregate(aggregate_process=RecordCount()) \
                .map(map_process=AppendString()) \
                .emit(emit_process=StdoutEmit(serializer=EmptySerializer()))
            
    # Add the stream to the context
    context.addStream(stream=stream)
    # Execute the stream. This in turn converts this graph to a PhysicalGraph for optimization, then to an ExecutionGraph for execution.
    context.execute()

# The entrypoint
if __name__ == "__main__":
    main()