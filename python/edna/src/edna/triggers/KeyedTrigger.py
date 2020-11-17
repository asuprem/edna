from edna.triggers import Trigger

class KeyedTrigger(Trigger):
    def __init__(self, key: object, value: object):
        self.key = key
        self.value = value
    
    def check(self, record: object) -> bool:
        if self.record[self.key] == self.value:
            return True
        return False