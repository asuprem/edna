from edna.triggers import Trigger

class CountTrigger(Trigger):
    def __init__(self, trigger_count: int):
        self.trigger_count = trigger_count
        # TODO --> build trigger later?
        self.count = 0

    def check(self, record: object) -> bool:
        self.count+=1
        if self.count == self.trigger_count:
            self.count = 0
            return True
        return False