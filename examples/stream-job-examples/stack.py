from edna.core.execution.context import StreamingContext
from edna.api import StreamBuilder
from edna.ingest.streaming import SimulatedIngest

from edna.serializers import EmptySerializer

from edna.emit import RecordCounterEmit
from edna.ingest.streaming.SimulatedIngest import SimulatedIngestCallable
import logging

import pdb


class streamgen(SimulatedIngestCallable):
    def compute_stream(self, index):
        return 'a'*10000000
    def hasNext(self, index) -> bool:
        return True


def main():

    logging.basicConfig(format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG, datefmt="%H:%M:%S")

    context = StreamingContext()
    
    # Ok, so we have a stream     
    stream = StreamBuilder.build(ingest=SimulatedIngest(serializer=EmptySerializer(), stream_callback=streamgen()), streaming_context=context)
    stream = stream.emit(emit_process=RecordCounterEmit(serializer=EmptySerializer(), record_print=1000))

    context.addStream(stream=stream)
    context.execute()
    #pdb.set_trace()

if __name__ == "__main__":
    main()