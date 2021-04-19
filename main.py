#! /usr/bin/env python2
# utf-8

import logging;logger = logging.getLogger("robots.main")

import argparse

import threading
import os
import sys
from os.path import abspath, dirname, join

import socket # to get my own ip
from Queue import Queue

from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine,qmlRegisterType
from PySide2.QtCore import QUrl, QObject, QTimer

from naoqibridge import NaoqiBridge, Person
from audiorecorder import AudioRecorder

from flask_server import tablet_webserver

# NEEDS TO BE IMPORTED *AFTER* tablet_webserver
# as new routes will be added to the Flask app for each activity
from supervisor import Supervisor


# taken from https://stackoverflow.com/a/28950776
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
            help="Naoqi port number (default: 9559)")

    parser.add_argument("--ssid", type=str, default="ECHOS-robot1",
                        help="Wifi SSID to which the robot's tablet should connect")

    parser.add_argument("--passwd", type=str, default="ECHOSechos",
                        help="Wifi password (assumes WPA)")


    args = parser.parse_args()




    ##################################################################
    #################### CONTROL INTERFACE ###########################

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

    ##################################################################


    ##################################################################
    ########################  TABLET WEB SERVER ######################

    port = int(os.environ.get('PORT', 8000))
    kwargs = {'host': '0.0.0.0', 'port': port , 'threaded' : True, 'use_reloader': False, 'debug':True}
    flask_thread = threading.Thread(target=tablet_webserver.run, kwargs=kwargs)
    flask_thread.setDaemon(True)
    flask_thread.start()

    bridge.connectTablet(args.ssid, "wpa", args.passwd)
    bridge.setTabletUrl("http://%s:%s/" % (get_ip(), port))
    ##################################################################


    ##################################################################
    ######################## SUPERVISOR ##############################

    supervisor = Supervisor(bridge)

    supervisor_thread = threading.Thread(target=supervisor.run)
    supervisor_thread.setDaemon(True)
    supervisor_thread.start()


    # share the supervisor's cmd_queue
    tablet_webserver.cmd_queue = supervisor.cmd_queue
    bridge.cmd_queue = supervisor.cmd_queue

    ##################################################################



    sys.exit(app.exec_())
