from __future__ import annotations


class BaseProcess(object):
    """BaseProcess is the base class for performing operations on streaming messages.

    Any child class must:
    
    - Implement the `process()` method
    
    - Call `super().__init__()` at the end of initialization
    
    Child classes should NOT:

    - modify the `__call__()` method
    """  
    def __init__(self, process: BaseProcess = None, *args, **kwargs) -> BaseProcess:
        """Initializes the Process primitive. It can take a Process primitive as input to chain them.

        Args:
            process (BaseProcess, optional): A process primitive for functional chaining.

        Returns:
            BaseProcess: A chained process primitive.
        """
        self.chained_process = process if process is not None else lambda x: x

    def __call__(self,message):
        """This is the entrypoint to this primitive to process a message. For example, you can do the following

        ```
        process = BaseProcess(*args)
        processed_message = process(message)
        ```

        Args:
            message (obj): A message to process with this primitive

        Returns:
            (obj): A processed message
        """
        return self.process(self.chained_process(message))
    
    def process(self, message):
        """Logic for message processing. Inheriting classes should implement this.

        Args:
            message (obj): The message to process with this logic

        Returns:
            (obj): A processed message
        """
        return message

__pdoc__ = {}
__pdoc__["BaseProcess.__call__"] = True