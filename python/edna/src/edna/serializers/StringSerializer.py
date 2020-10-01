from edna.serializers import Serializable
import msgpack

class StringSerializer(Serializable):

    @classmethod
    def read(cls, in_stream: bytes):
        return msgpack.unpackb(in_stream, encoding='utf-8')
    @classmethod
    def write(cls, out_stream: str):
        return msgpack.packb(out_stream, use_bin_type=True)