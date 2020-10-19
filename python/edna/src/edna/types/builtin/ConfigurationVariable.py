

class ConfigurationVariable(dict):
    """Wrapper around dict to store a single Configuration type.
    """
    def __getitem__(self, k: str):
        """Get a value from a key-value pair in the Configuration. Wrapper around dict.__getitem__()

        Args:
            k (str): Key for the desired key-value pair.

        Returns:
            (str): The value of the key-value pair.
        """
        return super().__getitem__(k)   # TODO return edna error?