# utf-8

import logging;logger = logging.getLogger("robots.supervisor")

from Queue import Queue

from PySide2.QtCore import QUrl, QObject

from websocketserver import TabletWebSocketServer


class Supervisor(QObject):
    def __init__(self):
        QObject.__init__(self)

        self.cmd_queue = Queue()

        # creates the websocket server to control the tablet content.
        # note that this server *must* run from the main thread (eg, the Qt app thread)
        self.tablet = TabletWebSocketServer()

    def run(self):

        while True:
            self.process_queue()

    def process_queue(self):

        source, cmd, args = self.cmd_queue.get()
        logger.info("GOT A %s CMD: %s (%s)" % (source, cmd, args))

        if source == "CTRL":
            self.tablet.setUrl("/")


