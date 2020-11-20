from edna.process.aggregate import Aggregate
from edna.process import BaseProcess
from edna.types.builtin import StreamRecord

class KeyedSum(Aggregate):
    process_name: str = "KeyedSum"    

    def __init__(self, key: str, process: BaseProcess = None, *args, **kwargs) -> BaseProcess:
        super().__init__(process=process, *args, **kwargs)
        self.key = key
        self.sum = 0
        self.triggeredEmit = [StreamRecord(0)]

    def aggregate(self, record: object):
        self.sum += record[self.key]
        self.triggeredEmit = [StreamRecord(self.sum)]


    def reset(self):
        self.sum = 0
        self.triggeredEmit = [StreamRecord(0)]