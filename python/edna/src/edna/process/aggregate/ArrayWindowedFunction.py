from __future__ import annotations
from typing import Dict, List
from edna.process.aggregate import Aggregate
from edna.process import BaseProcess
from edna.types.builtin import StreamRecord
class ArrayWindowedFunction(Aggregate):
    """WindowedFunction aggregates records and updates its internal state accordingly.
    When triggered, WindowedFunction will emit the aggregated state information stored 
    in `triggered_emit`
    """
    process_name: str = "ArrayWindowedFunction"    
    state: Dict[str,object]
    def __init__(self, build_configuration: Dict[str,str], process: BaseProcess = None, *args, **kwargs) -> BaseProcess:
        super().__init__(process=process, *args, **kwargs)
        self.triggeredEmit = []
        self.state = {}
        self.buildAggregatorState(build_configuration)

    def aggregate(self, record: object):
        self.triggeredEmit = [StreamRecord(record) for record in self.updateAggregatorState(record)]


    def updateAggregatorState(self, record: object) -> List[object]:
        raise NotImplementedError()
    
    def resetRecordAggregatorState(self):
        raise NotImplementedError()

    def buildAggregatorState(self, build_configuration: Dict[str,str]):
        raise NotImplementedError()

    def reset(self):
        self.triggeredEmit = []
        self.resetRecordAggregatorState()