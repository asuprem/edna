import enum

class SingleOutputStreamGraphNodeProcessType(enum.Enum):
    """Defines a `edna.core.plans.streamgraph.SingleOutputStreamGraphNode`'s node type.

    A MAP node wraps an `edna.process.Map`. It is a 1-to-1 transform that 
    emits 1 record for each record it receives.

    A FLATTEN node wraps an `edna.process.Flatten`. It is a 1-to-N transform that 
    flattens a stream of record collections to emit a stream of records..

    A FILTER node wraps an `edna.process.Filter`. Tt is an N-to-1 transform
    that can filter out some records it receives.

    An AGGREGATE node wraps an `edna.process.Aggregate`. It is something like
    an N-to-M transform, where multiple records can be aggregated before emitting
    a collection of records.
    """
    MAP = 1
    FLATTEN = 2
    FILTER = 3
    AGGREGATE = 4