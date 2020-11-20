from edna.process.aggregate import Aggregate
from edna.process import BaseProcess
from edna.types.builtin import StreamRecord
class KeyedMax(Aggregate):
    process_name: str = "KeyedMax"    

    def __init__(self, key: str, process: BaseProcess = None, *args, **kwargs) -> BaseProcess:
        super().__init__(process=process, *args, **kwargs)
        self.key = key
        self.max = -float("inf")
        self.triggeredEmit = [StreamRecord(self.max)]

    def aggregate(self, record: object):
        if record[self.key] > self.max:
            self.max = record[self.key]
            self.triggeredEmit = [StreamRecord(self.max)]


    def reset(self):
        self.max = -float("inf")
        self.triggeredEmit = [StreamRecord(self.max)]