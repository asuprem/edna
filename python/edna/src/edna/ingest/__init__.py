from __future__ import annotations
from edna.serializers import Serializable
from edna.core.types.enums import IngestPattern
class BaseIngest(object):
    execution_mode: IngestPattern
    def __init__(self, serializer: Serializable):
        self.serializer = serializer

from .iterable import IterableIngestBase
from .streaming import StreamingIngestBase
