from edna.core.configuration import EdnaConfiguration
from typing import Dict

class StreamingConfiguration(EdnaConfiguration):
    def set_variables(self, configuration: Dict[str, str]):
        for key in configuration["variables"]:
            self.setVariable(key, configuration["variables"][key])

    def set_options(self, configuration: Dict[str, str]):
        pass    # TODO add conf options for streaming configuration here