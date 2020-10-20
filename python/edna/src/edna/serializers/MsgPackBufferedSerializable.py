from edna.serializers import BufferedSerializable
import msgpack

class MsgPackBufferedSerializer(BufferedSerializable):
    serializer = msgpack.Packer().pack
    deserializer = msgpack.Unpacker()
    def __init__(self):
        pass

    def feed(self, buffered_message: bytes):
        self.deserializer.feed(buffered_message)

    def next(self):
        return next(self.deserializer)

    @classmethod
    def write(cls, out_stream):
        return cls.serializer(out_stream)



