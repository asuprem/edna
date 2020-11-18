# Triggers for aggregate emits...

# Triggers take in a record and determine, according to their memory, 
# if a record should trigger an emit on a  process
class Trigger:
    def __init__(self):
        pass

    def check(self, record: object) -> bool:
        return True


from .CountTrigger import CountTrigger
from .KeyedTrigger import KeyedTrigger
from .TimedTrigger import TimedTrigger