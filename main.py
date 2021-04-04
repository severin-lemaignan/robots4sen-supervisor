# utf-8


import argparse

import threading
import os
import sys
from os.path import abspath, dirname, join

from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine,qmlRegisterType

from naoqibridge import NaoqiBridge, Person
from audiorecorder import AudioRecorder

from flask_server import server

if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()


    app = QGuiApplication(sys.argv)
    qmlRegisterType(Person, 'Naoqi', 1, 0, 'Person')
    qmlRegisterType(AudioRecorder, 'Naoqi', 1, 0, 'AudioRecorder')
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


    port = int(os.environ.get('PORT', 8000))
    kwargs = {'host': '0.0.0.0', 'port': port , 'threaded' : True, 'use_reloader': False, 'debug':False}
    flask_thread = threading.Thread(target=server.run, kwargs=kwargs)
    flask_thread.setDaemon(True)
    flask_thread.start()



    sys.exit(app.exec_())
