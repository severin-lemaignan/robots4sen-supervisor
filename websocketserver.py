""" This file implements a simple websocket server to which the robot's
tablet connect. This makes it possible to instruct the tablet to go to
any webpage at any time (via `setUrl`), eg, to push content to the tablet.
"""

import logging;logger = logging.getLogger("robots.tablet_websocket")

from PySide2.QtCore import QUrl, QObject, Signal, Slot
from PySide2.QtWebSockets import QWebSocketServer
from PySide2.QtNetwork import QHostAddress

from helpers import get_ip

class TabletWebSocketServer(QObject):

    WS_PORT = 8080

    write = Signal(str)

    def __init__(self):
        QObject.__init__(self)

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


    def onNewConnection(self):
        self.clientConnection = self.server.nextPendingConnection()
        self.clientConnection.textMessageReceived.connect(self.processTextMessage)

        #self.clientConnection.binaryMessageReceived.connect(self.processBinaryMessage)
        self.clientConnection.disconnected.connect(self.socketDisconnected)

        logger.info("Tablet (re-)connecting")
        self.tablet = self.clientConnection

    
    def sendMsg(self, msg):
        if self.tablet:
            self.tablet.sendTextMessage(msg)
        else:
            logger.warning("Tablet not yet connected. Msg <%s> *not* sent." % msg)


    def setUrl(self, url):
        self.write.emit(url)

    def processTextMessage(self,  message):
        if (self.clientConnection):
            print("Received <%s>" % message)
            #self.clientConnection.sendTextMessage(message)

    #def processBinaryMessage(self,  message):
    #    if (self.clientConnection):
    #        self.clientConnection.sendBinaryMessage(message)

    def socketDisconnected(self):
        if (self.clientConnection):
            self.tablet = None
            self.clientConnection.deleteLater()


