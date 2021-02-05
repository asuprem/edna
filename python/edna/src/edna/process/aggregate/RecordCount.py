from edna.process.aggregate import Aggregate
from edna.process import BaseProcess
from edna.types.builtin import StreamRecord

class RecordCount(Aggregate):
    process_name: str = "RecordCount"    

    def __init__(self, process: BaseProcess = None, *args, **kwargs) -> BaseProcess:
        super().__init__(process=process, *args, **kwargs)
        self.count = 0
        self.triggeredEmit = [StreamRecord(0)]
        

    def aggregate(self, record: object):
        self.count += 1
        #print("Current count ---- ", self.count)
        self.triggeredEmit = [StreamRecord(self.count)]

    def reset(self):
        self.count = 0
        self.triggeredEmit = [StreamRecord(0)]