from edna.serializers import Serializable

class EmptyStringSerializer(Serializable):
    @classmethod
    def read(cls, in_stream: str):
        return in_stream
    @classmethod
    def write(cls, out_stream: str):
        return out_stream

class EmptyBoolSerializer(Serializable):
    @classmethod
    def read(cls, in_stream: bool):
        return in_stream
    @classmethod
    def write(cls, out_stream: bool):
        return out_stream

class EmptyIntSerializer(Serializable):
    @classmethod
    def read(cls, in_stream: int):
        return in_stream
    @classmethod
    def write(cls, out_stream: int):
        return out_stream

class EmptyFloatSerializer(Serializable):
    @classmethod
    def read(cls, in_stream: float):
        return in_stream
    @classmethod
    def write(cls, out_stream: float):
        return out_stream

class EmptyByteSerializer(Serializable):
    @classmethod
    def read(cls, in_stream: bytes):
        return in_stream
    @classmethod
    def write(cls, out_stream: bytes):
        return out_stream