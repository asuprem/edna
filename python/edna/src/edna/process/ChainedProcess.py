
from edna.process import BaseProcess
# TODO work on this and on StreamingContext physical graph


class ChainedProcess(BaseProcess):
    process_name : str = "ChainedProcess"
    def __init__(self, outer_process: BaseProcess, inner_process: BaseProcess, *args, **kwargs) -> BaseProcess:
        super().__init__(process=inner_process,  *args, **kwargs)
        self.outer_process = outer_process

    def process(self, record):
        return self.outer_process(record)
