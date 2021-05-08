# utf-8

import logging;logger = logging.getLogger("robots.supervisor")

from csv_logging import create_csv_logger

action_logger = create_csv_logger("logs/actions.csv") 

from Queue import Queue, Empty

from PySide2.QtCore import QUrl, QObject


from constants import *

###########################################
# ACTIVITIES
from activities.stories import activity as stories
from activities.mood_board import activity as moodboard

###########################################

TICK_PERIOD = 0.05 #sec

class Supervisor(QObject):
    def __init__(self, bridge):
        QObject.__init__(self)

        self.cmd_queue = Queue()

        self.bridge = bridge

        self.activity = None

    def run(self):

        while True:
            self.process_queue()
            if self.activity:
                status = self.activity.tick()
                if status == STOPPED:
                    logger.info("Activity <%s> completed" % self.activity)
                    action_logger.info((self.activity, status))
                    self.activity = None
                    self.bridge.tablet.default()

    def process_queue(self):

        try:
            source, cmd, args = self.cmd_queue.get(block=True, timeout=TICK_PERIOD)
        except Empty:
            return

        logger.info("GOT A %s CMD: %s (%s)" % (source, cmd, args))
        action_logger.info((source, cmd, args))
        
        if source == CTRL:
            if cmd == SOCIAL_GESTURE:
                self.bridge.animate(args)
            elif cmd == BEHAVIOUR:
                self.bridge.run_behaviour(args)
            elif cmd == LOOK_AT:
                self.bridge.lookAt(*args)
            elif cmd == TRACK:
                if not args:
                    self.bridge.stop_tracking()
                else:
                    self.bridge.track(args)
            elif cmd == ACTIVITY:
                    if args == "stories":
                        self.activity = stories.get_activity()
                        logger.info("Activity <%s> starting" % self.activity)
                        action_logger.info((self.activity, RUNNING))
                        self.activity.start(self.bridge)
                    elif args == "all_activities":
                        self.activity = moodboard.get_activity()
                        logger.info("Activity <%s> starting" % self.activity)
                        action_logger.info((self.activity, RUNNING))
                        self.activity.start(self.bridge, mood=None)

            else:
                logger.error("UNHANDLED CMD FROM %s: %s" % (source, cmd)) 
        elif source == TABLET:
            if cmd == ALL:
                pass
            else:
                logger.error("UNHANDLED CMD FROM %s: %s" % (source, cmd)) 
        else:
            logger.error("UNHANDLED CMD FROM %s: %s" % (source, cmd)) 


