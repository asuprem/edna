from __future__ import annotations
from edna.serializers import EmptySerializer
from edna.core.primitives import EdnaPrimitive
from edna.serializers import Serializable, BufferedSerializable
from edna.types.enums import IngestPattern
class BaseIngest(EdnaPrimitive):
    """BaseIngest is the base interface for ingesting records from various sources, 
    either external or internal (i.e. Kafka).

    Any child class must:

    - Call `super().__init__()` at the end of initialization
    
    - Create an `execution_mode` in `edna.core.types.enums.IngestPattern`
    
    - Create an execution pattern in the `run()` method of the correct 
        `edna.core.execution.context.EdnaContext`.
    """
    execution_mode: IngestPattern
    def __init__(self, serializer: Serializable, in_serializer: Serializable = None, out_serializer: BufferedSerializable = None, logger_name: str = None, *args, **kwargs):
        if serializer is None:
            serializer = EmptySerializer()
        if logger_name is None:
            logger_name = self.__class__.__name__
        super().__init__(serializer=serializer, in_serializer=in_serializer, out_serializer=out_serializer, logger_name=logger_name)

from .streaming import BaseStreamingIngest
