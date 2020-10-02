from edna.serializers import Serializable
import msgpack

class StringSerializer(Serializable):
    """Serializer for strings."""

    @classmethod
    def read(cls, in_stream: bytes):
        """Reads a string from a byte input.

        Args:
            in_stream (bytes): Input of bytes

        Returns:
            (str): Decoded bytes into utf-8 encoded strings
        """
        return msgpack.unpackb(in_stream, encoding='utf-8')
    @classmethod
    def write(cls, out_stream: str):
        """Writes an input string as a byte output.

        Args:
            out_stream (str): Input of string to output

        Returns:
            (byte): Encoded bytes from utf-8 encoded strings
        """
        return msgpack.packb(out_stream, use_bin_type=True)