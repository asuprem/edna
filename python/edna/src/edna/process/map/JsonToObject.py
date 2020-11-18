from edna.process.map import Map
import ujson

class JsonToObject(Map):
    """Maps a json formatted string to a Dictionary.

    Args:
        Map (BaseProcess): The interface this process implements
    """
    process_name : str = "JsonToObject"
    def map(self, record: str):
        return ujson.loads(record)