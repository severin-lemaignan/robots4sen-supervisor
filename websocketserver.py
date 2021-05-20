""" This file implements a simple websocket server to which the robot's
tablet connect. This makes it possible to instruct the tablet to go to
any webpage at any time (via `setUrl`), eg, to push content to the tablet.
"""

import logging;logger = logging.getLogger("robots.tablet_websocket")

from PySide2.QtCore import QUrl, QObject, Signal, Slot
from PySide2.QtWebSockets import QWebSocketServer
from PySide2.QtNetwork import QHostAddress

from Queue import Queue, Empty

import json

from constants import *
from helpers import get_ip

class TabletWebSocketServer(QObject):

    WS_PORT = 8080

    write = Signal(str)

    def __init__(self):
        QObject.__init__(self)

        self.response_queue = Queue()

        self.WS_IP = get_ip()

        self.server = QWebSocketServer("robotCtrl", QWebSocketServer.NonSecureMode)
        if self.server.listen(QHostAddress("0.0.0.0"), self.WS_PORT):
            logger.info('Connected: '+ self.server.serverName()+' : '+ str(self.WS_IP) +':'+str(self.server.serverPort()))
        else:
            logger.error('Error while starting the websocket server!')
            return


        self.server.newConnection.connect(self.onNewConnection)

        self.write.connect(self.sendMsg)

        # contains the socket to the tablet, once it connects
        self.tablet = None
        self.is_connected = False

    def isConnected(self):
        return self.is_connected

    def onNewConnection(self):
        if self.tablet:
            logger.warning("Attempting tablet connection, but I am already connected to a tablet!")
            logger.warning("...attempting to close previous socket")
            self.socketDisconnected()

        self.tablet = self.server.nextPendingConnection()
        self.tablet.textMessageReceived.connect(self.processTextMessage)
        self.tablet.disconnected.connect(self.socketDisconnected)

        logger.info("Trying to connect to tablet...")
        self.sendMsg(json.dumps({"type":"helo"}))
    
    def sendMsg(self, msg):
        if self.tablet:
            self.tablet.sendTextMessage(msg)
        else:
            logger.warning("Tablet not yet connected. Msg <%s> *not* sent." % msg)


    def default(self):
        # set the default 'wavy hand' animation
        self.write.emit(json.dumps({"type":"default"}))

    def debug(self, msg):
        self.write.emit(json.dumps({"type":"debug", "msg":msg}))

    def setUrl(self, url):
        self.write.emit(json.dumps({"type":"redirect", "url":url}))

    def clearOptions(self):
        self.write.emit(json.dumps({"type":"clear_options"}))

    def clearAll(self):
        """ Clears both options and (possible) footer.
        """ 
        self.write.emit(json.dumps({"type":"clear_all"}))

    def setOptions(self, options):
        self.write.emit(json.dumps({"type":"set_options", "options":options}))

    def showOption(self, id):
        self.write.emit(json.dumps({"type":"show_option", "id":id}))

    def addCancelBtn(self):
        btn = {"id": INTERRUPT, "img": "images/stop.svg", "label": "Stop", "footer": True}

        self.setOptions([btn])

    def yesNoBtns(self):
        btns = [
                {"id": YES, "img": "images/yes.svg", "label": "Yes"},
                {"id": NO, "img": "images/no.svg", "label": "No"}
               ]

        self.setOptions(btns)


    def isCancellationRequested(self):

        to_requeue = []
        while not self.response_queue.empty():
            action = self.response_queue.get()
            if action["id"] == INTERRUPT:
                return True
            else:
                # we've got an action from the tablet, but not a 'cancel' -> probably another
                # btn pressed. Save it to re-enqueue it later
                to_requeue.append(action)

        for a in to_requeue:
            self.response_queue.put(a)

        return False

    def processTextMessage(self,  raw):

        if (self.tablet):
            msg = json.loads(raw)

            if msg == "helo":
                logger.info("Tablet (re-)connected (port: %s)" % self.tablet.peerPort())
                self.is_connected = True
            else:
                logger.debug("Received [port %s]: <%s>" % (self.tablet.peerPort(), msg))
                if not self.response_queue.empty():
                    logger.warning("Tablet's response queue not empty! skipping the last mesage (%s)" % msg)
                else:
                    self.response_queue.put(msg)

    def socketDisconnected(self):
        if (self.tablet):
            self.tablet.deleteLater() # tell Qt to destroy the underlying Qt object
            self.tablet = None
            self.is_connected = False


