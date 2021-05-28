from constants import *

class Activity:

    type = "undefined"

    def __str__(self):
        return self.type

    def start(self):
        raise NotImplementedError()

    def tick(self, evt):
        raise NotImplementedError()

    def terminate(self):
        return STOPPED

