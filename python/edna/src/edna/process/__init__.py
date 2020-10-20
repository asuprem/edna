from __future__ import annotations

from edna.serializers import BufferedSerializable


class BaseProcess(object):
    """BaseProcess is the base class for performing operations on streaming messages.

    Any child class must:
    
    - Implement the `process()` method
    
    - Call `super().__init__()` at the end of initialization
    
    Child classes should NOT:

    - modify the `__call__()` method
    """  
    serializer: BufferedSerializable
    in_serializer: BufferedSerializable
    out_serializer: BufferedSerializable
    def __init__(self, process: BaseProcess = None, 
            serializer: BufferedSerializable = None, 
            in_serializer : BufferedSerializable = None, 
            out_serializer : BufferedSerializable = None, 
            *args, **kwargs) -> BaseProcess:
        """Initializes the Process primitive. It can take a Process primitive as input to chain them.

        Args:
            process (BaseProcess, optional): A process primitive for functional chaining.

        Returns:
            BaseProcess: A chained process primitive.
        """
        self.chained_process = process if process is not None else lambda x: x
        self.serializer = serializer
        if self.serializer is not None:
            self.in_serializer = in_serializer
            self.out_serializer = out_serializer
        else:
            self.in_serializer = self.serializer
            self.out_serializer = self.serializer

    def __call__(self, message):
        """This is the entrypoint to this primitive to process a message. For example, you can do the following

        ```
        process = BaseProcess(*args)
        processed_message = process(message)
        ```

        Args:
            message (List[obj]): A list of messages to process with this primitive. Usually Singleton unless the preceding is a 1-N mapping

        Returns:
            (obj): A processed message
        """
        for item in message:
            return self.process(self.chained_process(item))
    
    def process(self, message):
        """Logic for message processing. Inheriting classes should implement this. We return a singleton to work with Emit

        Args:
            message (obj): The message to process with this logic

        Returns:
            (obj): A processed message
        """
        return [message]

from .map import Map

__pdoc__ = {}
__pdoc__["BaseProcess.__call__"] = True