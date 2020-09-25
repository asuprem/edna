from __future__ import annotations

from edna.core.types.builtin import ConfigurationVariable
import yaml
from typing import Dict


class EdnaConfiguration:
    variables: ConfigurationVariable
    configuration: ConfigurationVariable
    options: ConfigurationVariable
    def __init__(self):
        self.variables = ConfigurationVariable()
    

    def setVariable(self, key: str, value): # TODO create an EdnaType, then add the default types to it??? for strict type checking?
        self.variables[key] = value
    
    def getVariable(self, key: str):
        return self.variables[key]

    def setOption(self, key: str, value): # TODO create an EdnaType, then add the default types to it??? for strict type checking?
        self.options[key] = value
    
    def getOption(self, key: str):
        return self.variables[key]


    def load_from_file(self, filepath: str):
        with open(filepath, "r") as conffile:
            temporary_configuration = yaml.load(conffile.read(), Loader=yaml.FullLoader)
        self.set_variables(temporary_configuration)
        self.set_options(temporary_configuration)
        #self.set_configuration(self, temporary_configuration)  # TODO record entire configuration???

    def set_variables(self, configuration: Dict[str, str]):
        """Set the internal variables in the configuration

        Args:
            configuration (Dict[str, str]): [The dictionary from the configuration yaml]
        """
        pass

    def set_options(self, configuration: Dict[str, str]):
        """Set the internal options for an EdnaContext using this Configuration class.

        Args:
            configuration (Dict[str, str]): [The dictionary from the configuration yaml]
        """
        pass



from .StreamingConfiguration import StreamingConfiguration