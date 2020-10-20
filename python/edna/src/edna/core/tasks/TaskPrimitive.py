import threading
import time
from edna.defaults import EdnaDefault


class TaskPrimitive(threading.Thread):
    def __init__(self, max_buffer_size : int = EdnaDefault.BUFFER_MAX_SIZE, 
            max_buffer_timeout : float = EdnaDefault.BUFFER_MAX_TIMEOUT_S):
        super().__init__()
        self.thread_stop = threading.Event()
        self.MAX_BUFFER_SIZE = max_buffer_size
        self.MAX_BUFFER_TIMEOUT_S = max_buffer_timeout
        self.BUFFER_POLL_TIMEOUT_S = EdnaDefault.POLL_TIMEOUT_S
        self.timer = time.time()

    # function using _stop function 
    def stop(self): 
        self.thread_stop.set() 
  
    def stopped(self): 
        return self.thread_stop.isSet() 

    def running(self):
        return not self.stopped()

    def shutdown(self):
        raise NotImplementedError