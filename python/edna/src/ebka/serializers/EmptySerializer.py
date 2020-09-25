from edna.serializers import Serializable

class EmptyStringSerializer(Serializable):
    def read(self, in_stream: str):
        return in_stream
    def write(self, out_stream: str):
        return out_stream

class EmptyBoolSerializer(Serializable):
    def read(self, in_stream: bool):
        return in_stream
    def write(self, out_stream: bool):
        return out_stream

class EmptyIntSerializer(Serializable):
    def read(self, in_stream: int):
        return in_stream
    def write(self, out_stream: int):
        return out_stream

class EmptyFloatSerializer(Serializable):
    def read(self, in_stream: float):
        return in_stream
    def write(self, out_stream: float):
        return out_stream

class EmptyByteSerializer(Serializable):
    def read(self, in_stream: bytes):
        return in_stream
    def write(self, out_stream: bytes):
        return out_stream