import threading
import time
from edna.defaults import EdnaDefault
import logging

class TaskPrimitive(threading.Thread):
    """A TaskPrimitive is the executable version of a PhysicalGraphNode. Each TaskPrimitive 
    runs on a separate thread, with communication between TaskPrimitives occuring through 
    `_BufferedEmit` and `_BufferedIngest`.

    Attributes:
        logger (logging.Logger): Logger for this TaskPrimitive
    """
    logger: logging.Logger
    def __init__(self, max_buffer_size : int = EdnaDefault.BUFFER_MAX_SIZE, 
            max_buffer_timeout : float = EdnaDefault.BUFFER_MAX_TIMEOUT_S,
            logger_name: str = None):
        """Initializes the TaskPrimitive. Sets up attributes and logger.

        Args:
            max_buffer_size (int, optional): The maximum size of the network buffers. 
                Defaults to EdnaDefault.BUFFER_MAX_SIZE.
            max_buffer_timeout (float, optional): The maximum timeout for the network buffers. 
                Defaults to EdnaDefault.BUFFER_MAX_TIMEOUT_S.
            logger_name (str, optional): Name for the logger. Defaults to None.
        """
        super().__init__()
        self.thread_stop = threading.Event()
        self.MAX_BUFFER_SIZE = max_buffer_size
        self.MAX_BUFFER_TIMEOUT_S = max_buffer_timeout
        self.BUFFER_POLL_TIMEOUT_S = EdnaDefault.POLL_TIMEOUT_S
        self.timer = time.time()
        if logger_name is None:
            self.logger = logging.getLogger(self.__class__.__name__)
        else:
            self.logger = logging.getLogger(logger_name)

    # function using _stop function 
    def stop(self):
        """Request this TaskPrimitive thread be stopped.
        """
        self.thread_stop.set() 
  
    def stopped(self) -> bool: 
        """Checks if a stop is requested.

        Returns:
            bool: Whether a stop is requested
        """
        return self.thread_stop.isSet() 

    def running(self) -> bool:
        """Checks if a stop is requested.

        Returns:
            bool: Whether the TaskPrimitive is supposed to keep running.
        """
        return not self.stopped()

    def shutdown(self):
        """Shut down the TaskPrimitive
        """
        raise NotImplementedError