# Triggers for aggregate emits...

# Triggers take in a record and determine, according to their memory, 
# if a message should trigger an emit ona  process
class Trigger:
    def __init__(self):
        raise NotImplementedError()

    def check(self, record: object) -> bool:
        raise NotImplementedError()


from .CountTrigger import CountTrigger
from .KeyedTrigger import KeyedTrigger
from .TimedTrigger import TimedTrigger