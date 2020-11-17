from edna.triggers import Trigger
import time

class TimedTrigger(Trigger):
    def __init__(self, trigger_time: int):
        self.trigger_time = trigger_time
        # TODO --> build trigger later?
        self.timer = time.time()

    def check(self, record: object) -> bool:
        if time.time() - self.timer > self.trigger_time:
            return True
        return False