from __future__ import annotations

from edna.core.configuration import EdnaConfiguration
from edna.ingest import BaseIngest
from edna.process import BaseProcess
from edna.emit import BaseEmit

import os

class EdnaContext:
    configuration: EdnaConfiguration
    ingest: BaseIngest
    process: BaseProcess
    emit: BaseEmit

    def __init__(self, dir : str = ".", confpath : str = "ednaconf.yaml", confclass: EdnaConfiguration = EdnaConfiguration):
        """[summary]

        Args:
            dir (str, optional): [Directory for the context.]. Defaults to "." for the current directory.
            conf (str, optional): [description]. Defaults to "ednaconf.yaml".
        """        
        self.configuration_path = os.path.join(dir, confpath)
        self.configuration = self.get_configuration(self.configuration_path, confclass)

    
    def get_configuration(self, confpath: str, confclass: EdnaConfiguration):
        # here we load from file. If file not exist, create a DefaultConfiguration
        configuration:EdnaConfiguration = confclass()
        if os.path.exists(confpath):
            configuration.load_from_file(confpath)
        return configuration

    def getVariable(self, key):
        return self.configuration.getVariable(key)

    def addIngest(self, ingest: BaseIngest):
        self.ingest = ingest
    
    def addProcess(self, process: BaseProcess):
        self.process = process

    def addEmit(self, emit: BaseEmit):
        self.emit = emit

    def execute(self):
        # TODO process optimizations go here in future
        self.run()

from .StreamingContext import StreamingContext