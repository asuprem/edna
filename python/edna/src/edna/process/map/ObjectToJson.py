from edna.process.map import Map
import ujson

class ObjectToJson(Map):
    """Maps an object to a json string.

    Args:
        Map (BaseProcess): The interface this process implements
    """
    process_name : str = "ObjectToJson"
    def map(self, record: str):
        return ujson.dumps(record)