from edna.core.execution.context import EdnaContext
from edna.core.configuration import StreamingConfiguration
from edna.core.types.enums import IngestPattern


class StreamingContext(EdnaContext):
    """A StreamingContext is the context for an EDNA job. It provides methods to control the job execution and to configure job variables.
    See docs for edna.core.execution.context.EdnaContext to initialize

    Args:
        EdnaContext ([Abstrract Base Class]): An abstract class for all Contexts that provides the interface for interacting with a Context.
    """        
    def __init__(self, dir : str = ".", confpath : str = "ednaconf.yaml", confclass: StreamingConfiguration = StreamingConfiguration):
        """Initialize the StreamingContext to accept an EDNA job graph and configuration.

        Args:
            dir (str, optional): [The directory for the job configuration]. Defaults to the current directory "."
            confpath (str, optional): [A YAML configuration file for the job. Job variables are loaded as top-level 
                fields from this file]. Defaults to "ednaconf.yaml".
            confclass (StreamingConfiguration, optional): [Object to store and interact with the Configuration]. 
                Defaults to edna.core.configuration.StreamingConfiguration.
        """        
        super().__init__(dir=dir, confpath=confpath, confclass=confclass)
    
    def run(self):  # TODO This should run on a separate thread to handle interrupts
        """This executes the a job for the StreamingContext. `run` is called through the `execute()` method in the interface.

        Raises:
            NotImplementedError: SERVER_SIDE_STREAM patterns are not implemented (and likely won't be, since the pattern is irrelevant)
        """        
        if self.ingest.execution_mode == IngestPattern.CLIENT_SIDE_STREAM:
            for streaming_item in self.ingest:  # This calls __next__
                self.emit(self.process(streaming_item)) # Serialization verification TODO
        if self.ingest.execution_mode == IngestPattern.SERVER_SIDE_STREAM:
            raise NotImplementedError
            

        
    

