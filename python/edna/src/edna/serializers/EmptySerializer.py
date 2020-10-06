from edna.serializers import Serializable

class EmptyObjectSerializer(Serializable):
    """EmptyObjectSerializer class expects obj and passes it.
    """
    @classmethod
    def read(cls, in_stream: object):
        return in_stream
    @classmethod
    def write(cls, out_stream: object):
        return out_stream

class EmptyStringSerializer(Serializable):
    """EmptyStringSerializer class expects str and passes it.
    """
    @classmethod
    def read(cls, in_stream: str):
        return in_stream
    @classmethod
    def write(cls, out_stream: str):
        return out_stream

class EmptyBoolSerializer(Serializable):
    """EmptyBoolSerializer class expects str and passes it.
    """
    @classmethod
    def read(cls, in_stream: bool):
        return in_stream
    @classmethod
    def write(cls, out_stream: bool):
        return out_stream

class EmptyIntSerializer(Serializable):
    """EmptyIntSerializer class expects str and passes it.
    """
    @classmethod
    def read(cls, in_stream: int):
        return in_stream
    @classmethod
    def write(cls, out_stream: int):
        return out_stream

class EmptyFloatSerializer(Serializable):
    """EmptyFloatSerializer class expects str and passes it.
    """
    @classmethod
    def read(cls, in_stream: float):
        return in_stream
    @classmethod
    def write(cls, out_stream: float):
        return out_stream

class EmptyByteSerializer(Serializable):
    """EmptyByteSerializer class expects str and passes it.
    """
    @classmethod
    def read(cls, in_stream: bytes):
        return in_stream
    @classmethod
    def write(cls, out_stream: bytes):
        return out_stream