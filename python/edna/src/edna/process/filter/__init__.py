from edna.process import BaseProcess


class Filter(BaseProcess):
    """A Filter Process filters the input. 

    Any child class must:
    
    - Implement the `filter()` method
    
    - Call `super().__init__()` at the end of initialization
    
    Child classes should NOT:

    - modify the `process()` method


    Args:
        BaseProcess (BaseProcess): A process to chain
    """
    def __init__(self, process: BaseProcess = None, *args, **kwargs) -> BaseProcess:
        """Initializes the Process primitive. It can take a Process primitive as input to chain them.

        Args:
            process (BaseProcess, optional): A process primitive for functional chaining.

        Returns:
            BaseProcess: A chained process primitive.
        """
        super().__init__(process=process,  *args, **kwargs)
    
    def process(self, message: object):
        """This is the entrypoint to this primitive to map a message. It is called by the BaseProcess parent
        from the `__call__()` method. It subsequently calls the `map()` method.

        This should NOT be modified.

        Args:
            message (obj): A message to process with this primitive

        Returns:
            (List[obj]): A processed message in a singleton list.
        """
        return [self.filter(message)]

    def filter(self, message: object):
        """Logic for mapping. Subclasses need to implement this.

        Args:
            message (obj): The message to process with this mapping logic

        Returns:
            (obj): A processed message
        """
        raise NotImplementedError()

from .KeyedFilter import KeyedFilter