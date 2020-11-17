from edna.process.aggregate import Aggregate
from edna.process import BaseProcess

class KeyedSum(Aggregate):
    process_name: str = "KeyedSum"    

    def __init__(self, key: str, process: BaseProcess = None, *args, **kwargs) -> BaseProcess:
        super().__init__(process=process, *args, **kwargs)
        self.key = key
        self.sum = 0
        self.triggeredEmit = 0

    def aggregate(self, record: object):
        self.sum += record[self.key]
        self.triggeredEmit = [self.sum]


    def reset(self):
        self.sum = 0
        self.triggeredEmit = [0]