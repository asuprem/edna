
from edna.ingest.streaming import BaseStreamingIngest
from edna.api.DataStream import DataStream
from edna.core.execution.context import StreamingContext


class StreamBuilder:
    """StreamBuilder takes in an edna ingest and builds a datastream with a root note.

    TODO -- update documentation. This is the entrypoint for a stream.
    """
    def __init__(self):
        """We don't need to do anything right now..."""
        pass

    def build(self, ingest: BaseStreamingIngest, streaming_context: StreamingContext, ingest_name: str = None):
        # This is where we build the DataStream object.
        return DataStream(ingest=ingest, streaming_context=streaming_context, ingest_name=ingest_name, stream_id=streaming_context.getDatastreamId())
