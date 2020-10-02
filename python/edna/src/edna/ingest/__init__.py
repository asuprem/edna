from __future__ import annotations
from edna.serializers import Serializable
from edna.core.types.enums import IngestPattern
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
    def __init__(self, serializer: Serializable):
        self.serializer = serializer

from .streaming import BaseStreamingIngest
