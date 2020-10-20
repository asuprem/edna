from __future__ import annotations
from edna.serializers import Serializable, BufferedSerializable
from edna.types.enums import IngestPattern
class BaseIngest(object):
    """BaseIngest is the base interface for ingesting messages from various sources, 
    either external or internal (i.e. Kafka).

    Any child class must:

    - Call `super().__init__()` at the end of initialization
    
    - Create an `execution_mode` in `edna.core.types.enums.IngestPattern`
    
    - Create an execution pattern in the `run()` method of the correct 
        `edna.core.execution.context.EdnaContext`.
    """
    execution_mode: IngestPattern
    serializer: Serializable
    in_serializer: Serializable
    out_serializer: BufferedSerializable
    def __init__(self, serializer: Serializable, in_serializer: Serializable = None, out_serializer: BufferedSerializable = None, *args, **kwargs):
        self.serializer = serializer
        if self.serializer is None:
            if in_serializer is None:
                raise ValueError("`in_serializer` cannot be None if serializer is `None` for Ingest Primitive")
            if out_serializer is None:
                raise ValueError("`in_serializer` cannot be None if serializer is `None` for Ingest Primitive")
            self.in_serializer = in_serializer
            self.out_serializer = out_serializer
        else:   # TODO does not check if serializer is a BufferedSerializable or Serializable
            self.in_serializer = self.serializer
            self.out_serializer = self.serializer

from .streaming import BaseStreamingIngest
