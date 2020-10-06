from edna.emit import SQLEmit
from typing import List, Tuple
from edna.serializers import Serializable
from edna.core.factories import SQLTupleFactory



class SQLUpsertEmit(SQLEmit):
    emit_buffer : List[Tuple]
    def __init__(self, serializer: Serializable, host: str, database: str, 
        user: str, password: str, table: str,
        tuple_factory: SQLTupleFactory,
        emit_buffer_batch_size: int = 10, emit_buffer_timeout_ms: int = 100):
        
        
        if tuple_factory.getUpsertCount() == 0:
            raise ValueError("Must pass upsert fields into SQLTupleFactory, got 0 upsert fields.")
        super().__init__(serializer=serializer, host=host, database=database,
            user=user, password=password, table=table, tuple_factory=tuple_factory, 
            emit_buffer_batch_size=emit_buffer_batch_size, emit_buffer_timeout_ms=emit_buffer_timeout_ms)
        
        

    def build_statement(self):
        if self.query_base is None:
        # TODO protect againsnt inject
            #TODO Finish this
            fields = ",".join(self.tuple_factory.getFields())
            value_types = ",".join(["%s"]*self.tuple_factory.getFieldCount())
            upsert = ",".join([" ".join([" ", item, "=", "VALUES(%s)"%item]) for item in self.tuple_factory.getUpsert()])   # UPDATE field = VALUES(field)
            self.query_base = "INSERT INTO {table} ({fields}) VALUES ({value_types}) ON DUPLICATE KEY UPDATE {upsert}".format(table=self.table, fields = fields, value_types = value_types, upsert=upsert)