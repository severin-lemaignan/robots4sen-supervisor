# utf-8


import argparse

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
logger = logging.getLogger("logger")

from enum import Enum
import sys
from os.path import abspath, dirname, join

from PySide2.QtCore import QUrl, Slot, Signal, QObject, Property, QTimer
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine

import qi

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

    def __init__(self, args):
        QObject.__init__(self)

        self._ip = args.ip
        self._port = str(args.port)
        self._session = qi.Session()

        self._connected = False
        self._plugged = False
        self._battery_level = 0.5

        self._watchdog_timer = QTimer(self)
        self._watchdog_timer.setInterval(NaoqiBridge.WATCHDOG_INTERVAL)
        self._watchdog_timer.timeout.connect(self.checkAlive)
        self._watchdog_timer.start()

        self.isConnected_changed.connect(self.on_isConnected_changed)

        self.connectToRobot()


    def connectToRobot(self):

        if self._connected:
            return True

        try:
            logger.info("Trying to connect to %s:%s..." % (self._ip, self._port))
            self._session.connect("tcp://" + self._ip + ":" + self._port)
        except RuntimeError:
            logger.error("Can't connect to Naoqi at ip \"" + self._ip + "\" on port " + self._port +".\n"
               "Please check your script arguments. Run with -h option for help.")
        
            self._connected = False
            return False

        self.almotion = self._session.service("ALMotion")
        self.albattery = self._session.service("ALBattery")
        self.almemory = self._session.service("ALMemory")
        self.alanimationplayer = self._session.service("ALAnimationPlayer")
        
        logger.info("Robot connected!")
        self._connected = True
        self.isConnected_changed.emit(self._connected)

        return True


    def checkAlive(self):

        if not self._connected:
            # try to reconnect...
            if not self.connectToRobot():
                return

        try:
            self._battery_level = self.albattery.getBatteryCharge()/100.
        except RuntimeError:
            if self._connected:
                logger.error("Robot disconnected!")
                self._connected = False
                self.isConnected_changed.emit(self._connected)
            return

        self.battery_changed.emit(self._battery_level)

        plugged = self.almemory.getData("Device/SubDeviceList/Battery/Charge/Sensor/Power") > 0
        if plugged != self._plugged:
            logger.warning("Robot plugged status = %s" % plugged)
            self._plugged = plugged
            self.isPlugged_changed.emit(self._plugged)



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


    @Slot(str)
    def animate(self, animation):
        """
        Argument is one of the available animation tag. See
        http://doc.aldebaran.com/2-5/naoqi/motion/alanimationplayer-advanced.html#animationplayer-tags-pepper
        """

        if not self._connected:
            logger.warning("Robot not connected. Can not perform 'animate'")
            return

        logging.debug("Running animation tag <%s>" % animation)
        future = self.alanimationplayer.runTag("hello", _async=True)
        future.value() # wait until the animation is complete


    @Slot(str, bool)
    def move(self, direction, active):

        if not self._connected:
            logger.warning("Robot not connected. Can not perform 'move'")
            return

        if direction == NaoqiBridge.STOP:
            self.almotion.stopMove()

        elif direction == NaoqiBridge.FORWARDS:
            if active:
                self.almotion.moveToward(0.6,0,0)
            else:
                self.almotion.stopMove()

        elif direction == NaoqiBridge.BACKWARDS:
            if active:
                self.almotion.moveToward(-0.4,0,0)
            else:
                self.almotion.stopMove()

        elif direction == NaoqiBridge.LEFT:
            if active:
                self.almotion.moveToward(0,0.3, 0)
            else:
                self.almotion.stopMove()

        elif direction == NaoqiBridge.RIGHT:
            if active:
                self.almotion.moveToward(0,-0.3, 0)
            else:
                self.almotion.stopMove()
        elif direction == NaoqiBridge.TURN_RIGHT:
            if active:
                self.almotion.moveToward(0,0, -0.3)
            else:
                self.almotion.stopMove()
        elif direction == NaoqiBridge.TURN_LEFT:
            if active:
                self.almotion.moveToward(0,0, 0.3)
            else:
                self.almotion.stopMove()

if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()


    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Instance of the Python object
    bridge = NaoqiBridge(args)

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
