import string, random

class NameUtils:
    @staticmethod
    def createNameSuffix(suffix_length=5):
        """Creates a suffix of random alphanumeric characters with the desired length.

        Args:
            suffix_length (int, optional): The length for the suffix. Defaults to 5.

        Returns:
            (str): A suffix of random alphanumeric characters.
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=5))

    @staticmethod
    def attachNameSuffix(name: str, suffix_length=5):
        """Creates a suffix of random alphanumeric characters with the desired length and
        appends it to the provided name.

        Args:
            name (str): The name value to append with a suffix
            suffix_length (int, optional): [description]. Defaults to 5.

        Returns:
            (str): A name combined with a suffix of random alphanumeric characters, separated by a dash ("-")
        """
        return name + "-" + NameUtils.createNameSuffix(suffix_length=suffix_length)