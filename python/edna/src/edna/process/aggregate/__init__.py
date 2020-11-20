from __future__ import annotations
from typing import List
from edna.process import BaseProcess
from edna.triggers import Trigger
from edna.types.builtin import StreamRecord

class Aggregate(BaseProcess):
    """An Aggregate Process gathers the input and aggregates them for other operations. 

    Any child class must:
    
    - Implement the `aggregate()` method
    
    - Call `super().__init__()` at the end of initialization
    
    Child classes should NOT:

    - modify the `process()` method


    Args:
        BaseProcess (BaseProcess): A process to chain
    """
    trigger: Trigger
    triggeredEmit: List[StreamRecord]
    process_name : str = "Aggregate"
    reset_flag : bool
    def __init__(self, process: BaseProcess = None, *args, **kwargs) -> BaseProcess:
        """Initializes the Process primitive. It can take a Process primitive as input to chain them.

        Args:
            process (BaseProcess, optional): A process primitive for functional chaining.

        Returns:
            BaseProcess: A chained process primitive.
        """
        super().__init__(process=process,  *args, **kwargs)
        self.trigger = Trigger() # The actual trigger
        self.triggeredEmit = None   # What is emitted when the aggregate is triggered
        self.reset_flag = True
    
    def process(self, record: object) -> List[StreamRecord]:
        """This is the entrypoint to this primitive to aggregate a record. It is called by the BaseProcess parent
        from the `__call__()` method. It subsequently calls the `aggregate()` method.

        This should NOT be modified.

        Args:
            record (obj): A record to process with this primitive

        Returns:
            (List[obj]): A processed record in a singleton list.
        """
        if self.reset_flag:
            self.resetAggregate()
        self.aggregate(record)
        return self.checkTrigger(record)


    def aggregate(self, record: object):
        """TODO Logic for aggregating. Subclasses need to implement this.

        Args:
            record (obj): The record to process with this aggregating logic
        """
        raise NotImplementedError()

    def addTrigger(self, trigger: Trigger):
        """TODO Add a trigger for this aggregate to start emitting.

        Args:
            trigger ([type]): [description]
        """
        self.trigger = trigger

    def checkTrigger(self, record: object) -> List[object]:
        if self.trigger.check(record):
            self.setResetFlag()
            return self.triggeredEmit
        else:
            return []

    def setResetFlag(self):
        self.reset_flag = True

    def unsetResetFlag(self):
        self.reset_flag = False

    def resetAggregate(self):
        self.unsetResetFlag()
        self.reset()
        

    def reset(self):
        raise NotImplementedError()



from .KeyedMax import KeyedMax
from .KeyedMaxBy import KeyedMaxBy
from .KeyedMin import KeyedMin
from .KeyedMinBy import KeyedMinBy
from .KeyedSum import KeyedSum