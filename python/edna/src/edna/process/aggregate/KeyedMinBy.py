from edna.process.aggregate import Aggregate
from edna.process import BaseProcess
from edna.types.builtin import StreamRecord

class KeyedMinBy(Aggregate):
    process_name: str = "KeyedMinBy"    

    def __init__(self, key: str, process: BaseProcess = None, *args, **kwargs) -> BaseProcess:
        super().__init__(process=process, *args, **kwargs)
        self.key = key
        self.min = float("inf")
        self.triggeredEmit = []

    def aggregate(self, record: object):
        if record[self.key] < self.min:
            self.min = record[self.key]
            self.triggeredEmit = [StreamRecord(record)]


    def reset(self):
        self.min = float("inf")
        self.triggeredEmit = []