""" This file implements a simple websocket server to which the robot's
tablet connect. This makes it possible to instruct the tablet to go to
any webpage at any time (via `setUrl`), eg, to push content to the tablet.
"""

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
logger = logging.getLogger("tablet_websocket")

from PySide2.QtCore import QUrl, QObject, Signal, Slot
from PySide2.QtWebSockets import QWebSocketServer
from PySide2.QtNetwork import QHostAddress


class TabletWebSocketServer(QObject):

    write = Signal(str)

    def __init__(self):
        QObject.__init__(self)

        self.server = QWebSocketServer("robotCtrl", QWebSocketServer.NonSecureMode)
        if self.server.listen(QHostAddress.LocalHost, 8080):
            print('Connected: '+self.server.serverName()+' : '+self.server.serverAddress().toString()+':'+str(self.server.serverPort()))
        else:
            print('error')
        self.server.newConnection.connect(self.onNewConnection)

        print(self.server.isListening())

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


