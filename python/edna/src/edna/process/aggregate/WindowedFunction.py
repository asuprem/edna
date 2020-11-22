from __future__ import annotations
from typing import Dict
from edna.process.aggregate import ArrayWindowedFunction
from edna.process import BaseProcess
from edna.types.builtin import StreamRecord
class WindowedFunction(ArrayWindowedFunction):
    """WindowedFunction aggregates records and updates its internal state accordingly.
    When triggered, WindowedFunction will emit the aggregated state information stored 
    in `triggered_emit`
    """
    process_name: str = "WindowedFunction"    
    state: Dict[str,object]

    def aggregate(self, record: object):
        self.triggeredEmit = [StreamRecord(self.updateAggregatorState(record))]

    def updateAggregatorState(self, record: object) -> object:
        raise NotImplementedError()