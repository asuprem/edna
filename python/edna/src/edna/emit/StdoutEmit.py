from edna.emit import BaseEmit

from sys import stdout

class StdoutEmit(BaseEmit):
    """An Emitter that writes to Stdout"""
    def write(self):
        """Writes the message to the standard output. Ideally, the message should be a string. This is useful only for debugging."""
        # NOT an efficient method, but really, who uses this for a real Job?
        for buffer_idx in range(self.emit_buffer_index+1):
            print(self.emit_buffer[buffer_idx], file=stdout)

        