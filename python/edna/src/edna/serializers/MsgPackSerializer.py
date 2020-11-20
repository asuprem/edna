from edna.serializers import Serializable
import msgpack

class MsgPackSerializer(Serializable):
    """Serializer for strings into and from Kafka. This is useful for debugging with 
    the console, because the console producers and consumers do not create messaegpack 
    objects."""

    @classmethod
    def read(cls, in_stream: bytes):
        """Reads a string from a byte input.

        Args:
            in_stream (bytes): Input of bytes

        Returns:
            (str): Decoded bytes into utf-8 encoded strings
        """
        return msgpack.unpackb(in_stream, raw=False)
    @classmethod
    def write(cls, out_stream: object):
        """Writes an input string as a byte output.

        Args:
            out_stream (object): Input of string to output

        Returns:
            (byte): Encoded bytes from utf-8 encoded strings
        """
        return msgpack.packb(out_stream, use_bin_type=True)
        