from edna.process.map import Map
import ujson

class JsonToObject(Map):
    """Maps a json formatted string to a Dictionary.

    Args:
        Map (BaseProcess): The interface this process implements
    """
    def map(self, message: str):
        return ujson.loads(message)