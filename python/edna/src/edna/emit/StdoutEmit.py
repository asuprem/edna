from edna.emit import BaseEmit

from sys import stdout

class StdoutEmit(BaseEmit):
    """An Emitter that writes to Stdout"""
    def write(self, message: str):
        """Writes the message to the standard output. Ideally, the message should be a string. THis is useful only for debugging.

        Args:
            message (str): The message to write
        """
        print(message, file=stdout)

        