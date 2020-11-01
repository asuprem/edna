from typing import Dict, List
from edna.process import BaseProcess
from edna.process.map import Map
from edna.core.factories import SQLTupleFactory
from abc import ABC


class ObjectToSQL(Map):
    """Maps an object to a Tuple of ((fields), (values)). This requires an 
    `edna.core.factories.SQLTupleFactory` instance to generate the SQL Tuples.

    You can use the existing class, which needs to be instansiated with the fields of the
    expected `SQLTuple`, or you can write your own TupleFactory that implements `getFields()`
    and `getValues()` method.
    
    Example usage:

        ```
        # Sample object to convert to SQLTuple
        >> employee_object = {"id": 10323, "employee_name": "Jonathan", "salary":100}
        # Build the Process
        >> tuple_factory = SQLTupleFactory(tuple_fields=["id","employee_name","salary"])
        >> obj_to_sql = ObjectToSQL(tuple_factory = tuple_factory)
        # Test the process
        >> obj_to_sql(employee_object)
        {"fields":("id","employee_name","salary"), "values":(10323, "Jonathan",100)}
        ```

    Args:
        Map (BaseProcess): The interface this process implements
    """
    process_name : str = "ObjectToSQL"
    def __init__(self, process: BaseProcess = None, 
        tuple_factory: SQLTupleFactory = None, 
        *args, **kwargs) -> BaseProcess:
        """Initializes the ObjectToSQL Map Operator with the provided `SQLTupleFactory` instance.

        Args:
            process (BaseProcess, optional): [description]. Defaults to None.
            tuple_factory (SQLTupleFactory.SQLTupleFactory, optional): [description]. Defaults to None.

        Returns:
            BaseProcess: [description]
        """
        if tuple_factory is None:
            raise ValueError("Must pass a `tuple_factory` instance to ObjectToSQL.__init__(), got None")
        self.tuple_factory = tuple_factory
        super().__init__(process=process, *args, **kwargs)


    def map(self, message: Dict):   # For Java, __init__ takes a TupleModel and a TupleFactory...
        """Returns a dictionary of "fields" and "values" for a SQLEmit emitter.

        Args:
            message (Dict): A record to process

        Returns:
            (Dict[str,tuple]): A dictionary with two keys, "fields" and "tuples", used by SQLEmit to insert into
                a database.
        """
        return self.tuple_factory.getValues(message=message)

        

