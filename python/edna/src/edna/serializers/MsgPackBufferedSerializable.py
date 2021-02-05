from edna.serializers import BufferedSerializable
import msgpack


class MsgPackBufferedSerializer(BufferedSerializable):
    #serializer = msgpack.Packer().pack
    serializer = msgpack.Packer().pack
    deserializer: msgpack.Unpacker
    def __init__(self):
        self.deserializer = msgpack.Unpacker()

    def feed(self, buffered_record: bytes):
        self.deserializer.feed(buffered_record)

    def next(self):
        return next(self.deserializer)

    @classmethod
    def write(cls, out_stream):
        return cls.serializer(out_stream)



