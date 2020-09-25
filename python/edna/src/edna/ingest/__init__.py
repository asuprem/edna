from edna.serializers import Serializable

class BaseIngest(object):
    def __init__(self, serializer: Serializable):
        self.serializer = serializer

from .iterable import IterableIngestBase
from .streaming import StreamingIngestBase
