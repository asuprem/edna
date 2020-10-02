from __future__ import annotations

from edna.exception import PrimitiveNotSetException
from edna.core.configuration import EdnaConfiguration
from edna.ingest import BaseIngest
from edna.process import BaseProcess
from edna.emit import BaseEmit
from abc import ABC
import os

class EdnaContext(ABC):
    """An EdnaContext is the generic context for any EdnaJob. It is an interface for the StreamingContext and other future contexts.

    Attributes:
        configuration (EdnaConfiguration): Stores a EdnaConfiguration object to control the job configuration.
        ingest (BaseIngest): Stores a reference to an ingest primitive.
        process (BaseProcess): Stores a reference to a process primitive.
        emit (BaseEmit): Stores a reference to an emit primitive

    Raises:
        PrimitiveNotSetException: Raises this exception if `execute()` is called without setting all of the primitives.
        
    Returns:
        EdnaContext: Returns an EdnaContext.
    """    
    configuration: EdnaConfiguration
    ingest: BaseIngest
    process: BaseProcess
    emit: BaseEmit

    def __init__(self, dir : str = ".", confpath : str = "ednaconf.yaml", confclass: EdnaConfiguration = EdnaConfiguration):
        """Initializes the EdnaContext with a directory, configuration file, and configuratioon object. 

        Args:
            dir (str, optional): The directory for the job configuration. Defaults to the current directory "."
            confpath (str, optional): A YAML configuration file for the job. Job variables are loaded as top-level 
                fields from this file. Defaults to "ednaconf.yaml".
            confclass (EdnaConfiguration, optional): Object to store and interact with the Configuration. 
                Defaults to edna.core.configuration.StreamingConfiguration.
        """                
        self.dir = dir
        self.configuration_path = os.path.join(self.dir, confpath)
        self.configuration = self._get_configuration(self.configuration_path, confclass)

    
    def _get_configuration(self, confpath: str, confclass: EdnaConfiguration):
        """Sets up a

        Args:
            confpath (str): Absolute path to the configuration file.
            confclass (EdnaConfiguration): The specific class of the resulting EdnaConfiguration, i.e. StreamingConfiguration.

        Returns:
            EdnaConfiguration: Returns an EdnaConfiguration object.
        """        
        # here we load from file. If file not exist, create a DefaultConfiguration
        configuration:EdnaConfiguration = confclass()
        if os.path.exists(confpath):
            configuration.load_from_file(confpath)
        return configuration

    def getVariable(self, key: str):
        """Returns a value from a key-value pair from the stored EdnaConfiguration

        Args:
            key (str): The key to search the EdnaConfiguration

        Returns:
            Object: The value associated with the key in the EdnaConfiguration.
        """        
        return self.configuration.getVariable(key)

    def addIngest(self, ingest: BaseIngest):
        """Adds the provided ingest primitive to the EdnaContext

        Args:
            ingest (BaseIngest): Ingest primitive for the EdnaContext
        """
        self.ingest = ingest
    
    def addProcess(self, process: BaseProcess):
        """Adds the provided process primitive to the EdnaContext

        Args:
            ingest (BaseProcess): Process primitive for the EdnaContext
        """
        self.process = process

    def addEmit(self, emit: BaseEmit):
        """Adds the provided emit primitive to the EdnaContext

        Args:
            ingest (BaseEmit): Emit primitive for the EdnaContext
        """
        self.emit = emit

    def execute(self):
        """Execute the EdnaContext. This calls the `run()` method, which must be implemented in the inheriting class.

        Raises:
            PrimitiveNotSetException: Raises this exception if `execute()` is called without setting all of the primitives.
        """
        # TODO process optimizations go here in future
        if self.ingest is None:
            raise PrimitiveNotSetException("StreamingContext", "Ingest")
        if self.process is None:
            raise PrimitiveNotSetException("StreamingContext", "Process")
        if self.emit is None:
            raise PrimitiveNotSetException("StreamingContext", "Emit")
        self.run()

from .StreamingContext import StreamingContext