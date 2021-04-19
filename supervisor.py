# utf-8

import logging;logger = logging.getLogger("robots.supervisor")

from Queue import Queue

from PySide2.QtCore import QUrl, QObject

from websocketserver import TabletWebSocketServer

from constants import *

###########################################
# ACTIVITIES
from activities.stories import activity as stories

###########################################

class Supervisor(QObject):
    def __init__(self, bridge):
        QObject.__init__(self)

        self.cmd_queue = Queue()

        self.bridge = bridge

        # creates the websocket server to control the tablet content.
        # note that this server *must* run from the main thread (eg, the Qt app thread)
        self.tablet = TabletWebSocketServer()

    def run(self):

        while True:
            self.process_queue()

    def process_queue(self):

        source, cmd, args = self.cmd_queue.get()
        logger.info("GOT A %s CMD: %s (%s)" % (source, cmd, args))

        if source == CTRL:
            if cmd == SOCIAL_GESTURE:
                self.bridge.animate(args)
            elif cmd == LOOK_AT:
                self.bridge.lookAt(*args)
            elif cmd == TRACK:
                if not args:
                    self.bridge.stop_tracking()
                else:
                    self.bridge.track(args)
            else:
                logger.error("UNHANDLED CMD FROM %s: %s" % (source, cmd)) 
        else:
            logger.error("UNHANDLED CMD FROM %s: %s" % (source, cmd)) 


