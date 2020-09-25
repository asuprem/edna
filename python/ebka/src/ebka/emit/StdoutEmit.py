from ebka.emit import BaseEmit

from sys import stdout

class StdoutEmit(BaseEmit):
    """An Emitter that writes to stdout"""
    def write(self, message):
        print(message, file=stdout)

        