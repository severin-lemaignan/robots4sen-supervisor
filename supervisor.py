# utf-8

import logging;logger = logging.getLogger("robots.supervisor")

from csv_logging import create_csv_logger

action_logger = create_csv_logger("actions.csv") 

from Queue import Queue, Empty

from PySide2.QtCore import QUrl, QObject

from websocketserver import TabletWebSocketServer

from constants import *

###########################################
# ACTIVITIES
from activities.stories import activity as stories

###########################################

TICK_PERIOD = 0.05 #sec

class Supervisor(QObject):
    def __init__(self, bridge):
        QObject.__init__(self)

        self.cmd_queue = Queue()

        self.bridge = bridge

        # creates the websocket server to control the tablet content.
        # note that this server *must* run from the main thread (eg, the Qt app thread)
        self.tablet = TabletWebSocketServer()

        self.activity = None

    def run(self):

        while True:
            self.process_queue()
            if self.activity:
                status = self.activity.tick()
                if status == STOPPED:
                    logger.info("Activity <%s> completed" % self.activity)
                    action_logger.info("%s, %s, %s" % (self.activity, status))
                    self.activity = None

    def process_queue(self):

        try:
            source, cmd, args = self.cmd_queue.get(block=True, timeout=TICK_PERIOD)
        except Empty:
            return

        logger.info("GOT A %s CMD: %s (%s)" % (source, cmd, args))
        action_logger.info("%s, %s, %s" % (source, cmd, args))

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
            else:
                logger.error("UNHANDLED CMD FROM %s: %s" % (source, cmd)) 
        elif source == TABLET:
            if cmd == STORIES:
                self.activity = stories.get_activity()
                logger.info("Activity <%s> starting" % self.activity)
                action_logger.info("%s, %s, %s" % (self.activity, RUNNING))
                self.activity.start(self.tablet, self.bridge)
        else:
            logger.error("UNHANDLED CMD FROM %s: %s" % (source, cmd)) 


