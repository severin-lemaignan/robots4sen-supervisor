# utf-8

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
logger = logging.getLogger("logger")

from enum import Enum
import sys
from os.path import abspath, dirname, join

from PySide2.QtCore import QUrl, Slot, QObject, QEnum
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine

class NaoqiBridge(QObject):

    STOP = "STOP"
    FORWARDS = "FORWARDS"
    BACKWARDS = "BACKWARDS"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    TURN_LEFT = "TURN_LEFT"
    TURN_RIGHT = "TURN_RIGHT"

    @Slot(str, bool)
    def move(self, direction, active):

        if direction == NaoqiBridge.STOP:
            logger.info("Stopping now")

        elif direction == NaoqiBridge.FORWARDS:
            if active:
                logger.info("Starting moving forward")
            else:
                logger.info("Stopping moving forward")

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
