

class ConfigurationVariable(dict):
    def __getitem__(self, k):
        return super().__getitem__(k)   # TODO return edna error?