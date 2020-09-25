from __future__ import annotations


class BaseProcess(object):
    """BaseProcess is the base class for performing operations on streaming messages.

    Any edna.process function inherits from BaseProcess and must implement the process() function.

    If the subclass overrides the constructor, it must make sure to invoke the base class constructor 
    before finishing.
    """  
    def __init__(self, process: BaseProcess = None) -> BaseProcess:
        self.chained_process = process if process is not None else lambda x: x

    def __call__(self,message):
        return self.process(self.chained_process(message))
    
    def process(self, message):
        return message