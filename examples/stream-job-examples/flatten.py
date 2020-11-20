from edna.core.execution.context import StreamingContext
from edna.api import StreamBuilder
from edna.ingest.streaming import SimulatedIngest

from edna.serializers import EmptySerializer

from edna.emit import StdoutEmit
from edna.ingest.streaming.SimulatedIngest import SimulatedIngestCallable
from edna.process.flatten import StringFlatten
import logging

import random


class streamgen(SimulatedIngestCallable):
    def compute_stream(self, index):
        repeat=random.randint(1,4)
        return ' '.join([chr(index%26+97)*repeat]*repeat)
    def hasNext(self, index) -> bool:
        return True


def main():

    logging.basicConfig(format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG, datefmt="%H:%M:%S")

    context = StreamingContext()
    
    # Ok, so we have a stream     
    stream = StreamBuilder.build(ingest=SimulatedIngest(serializer=EmptySerializer(), stream_callback=streamgen(), watermark_timer = 1), streaming_context=context)
    stream = stream.flatten(flatten_process=StringFlatten(separator=" ")) \
                .emit(emit_process=StdoutEmit(serializer=EmptySerializer()))

    context.addStream(stream=stream)
    context.execute()
    #pdb.set_trace()

if __name__ == "__main__":
    main()