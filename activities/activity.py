import logging
logger = logging.getLogger("robots.activity")

from csv_logging import create_csv_logger
action_logger = create_csv_logger("logs/actions.csv") 


from events import Event
from constants import *

class Activity(object):

    type = "undefined"

    def __init__(self):
        pass

    def __str__(self):
        return self.type

    def start(self, robot, cmd_queue):
       
        self.robot = robot
        self.cmd_queue = cmd_queue
        self.response_queue = self.robot.tablet.response_queue

        self.robot.tablet.debug("activity/%s" % self)
        action_logger.info((str(self),RUNNING))
 
        # self._behaviour is a generator returning the current activity status;
        # self.tick() (called by the supervisor) will progress through it
        self._behaviour = self.run()

    def run(self):
        raise NotImplementedError()

    def tick(self, evt=None):
        """
        returns: RUNNING while running, FINISHED once finished
        """

        if evt:
            if evt.type == Event.INTERRUPTED:
                return self.on_interrupted(evt)
            if evt.type == Event.NO_ONE_ENGAGED:
                return self.on_no_one_engaged(evt)
            if evt.type == Event.NO_INTERACTION:
                return self.on_no_interaction(evt)

        try:
            return next(self._behaviour)
        except StopIteration:
            action_logger.info((str(self),FINISHED))
            return FINISHED


    def on_interrupted(self, evt):
        logger.warning("Activity <%s> interrupted: %s" % (self, evt));
        action_logger.info((str(self),str(evt)))
        return self.terminate()

    def on_no_one_engaged(self, evt):
        logger.warning("Activity <%s> interrupted: %s" % (self, evt));
        action_logger.info((str(self),str(evt)))
        return self.terminate()

    def on_no_interaction(self, evt):
        logger.warning("Activity <%s> interrupted: %s" % (self, evt));
        action_logger.info((str(self),str(evt)))
        return self.terminate()

    def terminate(self):
        return INTERRUPTED

