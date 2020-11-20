from __future__ import annotations

from edna.serializers import BufferedSerializable
from typing import List
from edna.core.primitives import EdnaPrimitive
from edna.types.builtin import StreamRecord, RecordCollection

class BaseProcess(EdnaPrimitive):
    """BaseProcess is the base class for performing operations on streaming records.

    Any child class must:
    
    - Implement the `process()` method
    
    - Call `super().__init__()` at the end of initialization
    
    Child classes should NOT:

    - modify the `__call__()` method
    """  
    process_name : str = "BaseProcess"
    process: BaseProcess
    chained_process: BaseProcess
    
    def __init__(self, process: BaseProcess = None, 
            serializer: BufferedSerializable = None, 
            in_serializer : BufferedSerializable = None, 
            out_serializer : BufferedSerializable = None, 
            logger_name: str = None,
            *args, **kwargs) -> BaseProcess:
        """Initializes the Process primitive. It can take a Process primitive as input to chain them.

        Args:
            process (BaseProcess, optional): A process primitive for functional chaining.

        Returns:
            BaseProcess: A chained process primitive.
        """
        if logger_name is None:
            logger_name = self.__class__.__name__
        super().__init__(serializer=serializer, in_serializer=in_serializer, out_serializer=out_serializer, logger_name=logger_name)
        self.replaceChainedProcess(process)

    def __call__(self, record: RecordCollection[StreamRecord]) -> RecordCollection[StreamRecord]:
        """This is the entrypoint to this primitive to process a record. For example, you can do the following

        ```
        process = BaseProcess(*args)
        processed_record = process(record)
        ```

        Args:
            record (List[obj]): A list of record to process with this primitive. Usually Singleton unless the preceding is a 1-N mapping

        Returns:
            (obj): A processed record
        """
        complete_results = RecordCollection([])   # TODO Update this to a RecordCollecton
        intermediate_result = self.chained_process(record)    # Returns a list
        #if self.process_name == "ObjectToJson":
        for stream_record in intermediate_result:    # is a list
            complete_results += self.process(stream_record.getValue())
        return complete_results


    def process(self, record: object) -> List[StreamRecord]:
        """Logic for record processing. Inheriting classes should implement this. We return a singleton to work with Emit

        Args:
            record (obj): The record to process with this logic

        Returns:
            (obj): A processed record
        """
        return [StreamRecord(record)]

    def replaceChainedProcess(self, process: BaseProcess = None):
        self.chained_process = process if process is not None else lambda x: x


__pdoc__ = {}
__pdoc__["BaseProcess.__call__"] = True