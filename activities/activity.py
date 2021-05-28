import logging
logger = logging.getLogger("robots.activity")

from events import Event
from constants import *

class Activity(object):

    type = "undefined"

    def __init__(self):

        # self._behaviour is a generator returning the current activity status;
        # self.tick() (called by the supervisor) will progress through it
        self._behaviour = self.run()

    def __str__(self):
        return self.type

    def start(self):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()

    def tick(self, evt=None):
        """
        returns: RUNNING while running, STOPPED once finished
        """

        if evt:
            if evt.type == Event.INTERRUPTED:
                return self.on_interrrupted(evt)
            if evt.type == Event.NO_ONE_ENGAGED:
                return self.on_no_one_engaged(evt)
            if evt.type == Event.NO_INTERACTION:
                return self.on_no_interaction(evt)

        try:
            return next(self._behaviour)
        except StopIteration:
            return STOPPED


    def on_interrrupted(self, evt):
        logger.warning("Activity <%s> interrupted: %s" % (self, evt));
        return self.terminate()

    def on_no_one_engaged(self, evt):
        logger.warning("Activity <%s> interrupted: %s" % (self, evt));
        return self.terminate()

    def on_no_interaction(self, evt):
        logger.warning("Activity <%s> interrupted: %s" % (self, evt));
        return self.terminate()

    def terminate(self):
        return STOPPED

