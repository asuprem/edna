from edna.serializers import Serializable

class EmptySerializer(Serializable):
    """EmptySerializer class expects obj and passes it.
    """
    @classmethod
    def read(cls, in_stream: object):
        return in_stream
    @classmethod
    def write(cls, out_stream: object):
        return out_stream

