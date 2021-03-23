# utf-8

import math

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
logger = logging.getLogger("logger")

from enum import Enum
import sys
from os.path import abspath, dirname, join

from PySide2.QtCore import QUrl, Slot, Signal, QObject, Property, QTimer
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine

class NaoqiBridge(QObject):

    WATCHDOG_INTERVAL = 200 #ms

    STOP = "STOP"
    FORWARDS = "FORWARDS"
    BACKWARDS = "BACKWARDS"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    TURN_LEFT = "TURN_LEFT"
    TURN_RIGHT = "TURN_RIGHT"

    isConnected_changed = Signal(bool)
    isPlugged_changed = Signal(bool)
    battery_changed = Signal(float)

    def __init__(self):
        QObject.__init__(self)

        self._connected = False
        self._plugged = False
        self._battery_level = 0.5

        self._watchdog_timer = QTimer(self)
        self._watchdog_timer.setInterval(NaoqiBridge.WATCHDOG_INTERVAL)
        self._watchdog_timer.timeout.connect(self.checkAlive)
        self._watchdog_timer.start()

        self.isConnected_changed.connect(self.on_isConnected_changed)
        self.count = 0


    def checkAlive(self):

        self._battery_level = (math.sin(self.count/10) + 1) / 2
        self.battery_changed.emit(self._battery_level)

        if self.count < 5:
            if self._connected != True:
                self._connected = True
                self.isConnected_changed.emit(self._connected)

                print("Connected")
        else:
            if self._connected != False:
                print("Disconnected")
                self._connected = False
                self.isConnected_changed.emit(self._connected)
            
        self.count += 1


    @Property(bool, notify=isConnected_changed)
    def connected(self):
        return self._connected

    @Property(bool, notify=isPlugged_changed)
    def plugged(self):
        return self._plugged

    @Property(float, notify=battery_changed)
    def battery(self):
        return self._battery_level

    @Slot()
    def on_isConnected_changed(self, value):
        logging.warning("Connection status changed! connected=%s" % value)


    @Slot(str, bool)
    def move(self, direction, active):

        if direction == NaoqiBridge.STOP:
            logger.info("Stopping now")

        elif direction == NaoqiBridge.FORWARDS:
            if active:
                logger.info("Starting moving forward")
            else:
                logger.info("Stopping moving forward")

        elif direction == NaoqiBridge.BACKWARDS:
            if active:
                logger.info("Starting moving backward")
            else:
                logger.info("Stopping moving backward")

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Instance of the Python object
    bridge = NaoqiBridge()

    # Expose the Python object to QML
    context = engine.rootContext()
    context.setContextProperty("naoqi", bridge)


    # Get the path of the current directory, and then add the name
    # of the QML file, to load it.
    qmlFile = join(dirname(__file__), 'main.qml')
    engine.load(abspath(qmlFile))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())
