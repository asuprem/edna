
from edna.ingest.streaming import BaseStreamingIngest
from edna.api.DataStream import DataStream
from edna.core.execution.context import StreamingContext


class StreamBuilder:
    """StreamBuilder is the factory method to build a new DataStream. Call `StreamBuilder.build()` to
    build a new DataStream.
    """

    @classmethod
    def build(cls, ingest: BaseStreamingIngest, streaming_context: StreamingContext, ingest_name: str = None) -> DataStream:
        """Builds a new DataStream.

        Args:
            ingest (BaseStreamingIngest): The ingest primitive for this DataStream
            streaming_context (StreamingContext): The context for this DataStream
            ingest_name (str, optional): The name for this ingest node. Defaults to None.

        Returns:
            DataStream: Returns a DataStream instance.
        """
        # This is where we build the DataStream object.
        return DataStream(  ingest=ingest, 
                            streaming_context=streaming_context, 
                            ingest_name=ingest_name, 
                            stream_id=streaming_context.getDatastreamId())
