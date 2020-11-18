import abc
from typing import Dict, List

class SQLTupleFactory(abc.ABC):
    def __init__(self, tuple_fields: List[str], upsert_fields: List[str] = None):
        """Initializes the Factory with the tuple_model. TODO update documentation

        Args:
            tuple_fields (List[str]): A List of strings corresponding to keys in the object
                that `ObjectToSQL` will convert into a SQL Tuple.
        """
        self.field_tuple = tuple(tuple_fields)
        self.field_len = len(self.field_tuple)
        if upsert_fields is not None:
           self.upsert_tuple = tuple(upsert_fields)
           self.upsert_len = len(self.upsert_tuple)
        else:
            self.upsert_tuple = None
            self.upsert_len = 0


    def getFields(self):
        """Getter for `field_tuple`

        Returns:
            (Tuple): `field_tuple`
        """
        return self.field_tuple

    def getUpsert(self):
        return self.upsert_tuple

    def getValues(self, record: Dict):
        """Extracts a tuple of values from the record using `field_tuple`'s fields.
        This can be overridden for efficiency to hardcode an object model.

        Args:
            record (obj): A record to process
        Returns:
            (Tuple): A Tuple of all values corresponding to the `field_tuple`
        """
        values_list = [None]*self.field_len
        for idx,field in enumerate(self.field_tuple):
            values_list[idx] = record[field]
        return tuple(values_list)

    def getFieldCount(self):
        return self.field_len
    def getUpsertCount(self):
        return self.upsert_len
        
        
    