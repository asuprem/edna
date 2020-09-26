from edna.core.execution.context import EdnaContext
from edna.core.configuration import StreamingConfiguration
from edna.core.types.enums import IngestPattern


class StreamingContext(EdnaContext):

    def __init__(self, dir : str = ".", confpath : str = "ednaconf.yaml", confclass: StreamingConfiguration = StreamingConfiguration):
        super().__init__(dir=dir, confpath=confpath, confclass=confclass)
    
    def run(self):  # TODO This should run on a separate thread to handle interrupts
        """This executes the Edna Context containing the Ingest, Process, and Emit primitives
        """
        if self.ingest.execution_mode == IngestPattern.CLIENT_SIDE_STREAM:
            for streaming_item in self.ingest:  # This calls __next__
                self.emit(self.process(streaming_item)) # Serialization verification TODO
        if self.ingest.execution_mode == IngestPattern.SERVER_SIDE_STREAM:
            raise NotImplementedError
            

        
    

