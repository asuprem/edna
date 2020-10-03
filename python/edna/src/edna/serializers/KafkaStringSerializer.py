from edna.serializers import Serializable
import codecs

class KafkaStringSerializer(Serializable):
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
        return codecs.decode(in_stream, encoding="utf-8")
    @classmethod
    def write(cls, out_stream: str):
        """Writes an input string as a byte output.

        Args:
            out_stream (str): Input of string to output

        Returns:
            (byte): Encoded bytes from utf-8 encoded strings
        """
        return bytes(out_stream, encoding="utf-8")
        