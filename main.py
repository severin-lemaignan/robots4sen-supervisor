#! /usr/bin/env python2
# utf-8



import logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("robots.main")

import coloredlogs
coloredlogs.install(level=logging.DEBUG)


import argparse
import time
import threading
import os
import sys 
sys.path.append("/home/echos/nao/pynaoqi-python2.7-2.5.7.1-linux64/lib/python2.7/site-packages")
from os.path import abspath, dirname, join

from Queue import Queue

from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine,qmlRegisterType
from PySide2.QtCore import QUrl, QObject, QTimer

from helpers import get_ip

from naoqibridge import NaoqiBridge, Person
from audiorecorder import AudioRecorder

from flask_server import tablet_webserver

# NEEDS TO BE IMPORTED *AFTER* tablet_webserver
# as new routes might be added to the Flask app for each activity
from supervisor import Supervisor

if __name__ == "__main__":

    from remote_debug import listen
    listen()

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
            help="Naoqi port number (default: 9559)")

    parser.add_argument("--ssid", type=str, default="ECHOS-robot1",
                        help="Wifi SSID to which the robot's tablet should connect")

    parser.add_argument("--passwd", type=str, default="",
                        help="Wifi password (assumes WPA)")

    parser.add_argument("--force-tablet-reconnection", action="store_true",
                        help="Force a reconnection of Pepper's tablet, even if already connected.")

    parser.add_argument("--no-tablet", action="store_true", help="[debug] Do not use Pepper's tablet")
    parser.add_argument("--no-control-ui", action="store_true", help="[debug] Do not start the control iterface")
    parser.add_argument("--no-robot", action="store_true", help="[debug] Run without a robot, simulated or real")

    args = parser.parse_args()




    ##################################################################
    #################### CONTROL INTERFACE ###########################
    
    if not args.no_control_ui:

        app = QGuiApplication(sys.argv)
        qmlRegisterType(Person, 'Naoqi', 1, 0, 'Person')
        qmlRegisterType(AudioRecorder, 'Naoqi', 1, 0, 'AudioRecorder')
        engine = QQmlApplicationEngine()

    # Instance of the Python object
    bridge = NaoqiBridge(args)


    if not args.no_control_ui:
        # Expose the Python object to QML
        context = engine.rootContext()
        context.setContextProperty("naoqi", bridge)

    ##################################################################


    ##################################################################
    ########################  TABLET WEB SERVER ######################

    if not args.no_tablet:
        port = int(os.environ.get('PORT', 8000))
        kwargs = {'host': '0.0.0.0', 'port': port , 'threaded' : True, 'use_reloader': False, 'debug':True}
        flask_thread = threading.Thread(target=tablet_webserver.run, kwargs=kwargs)
        flask_thread.setDaemon(True)
        flask_thread.start()

        bridge.connectTablet(args.ssid, "wpa", args.passwd, args.force_tablet_reconnection)
    ##################################################################


    ##################################################################
    ######################## SUPERVISOR ##############################

    supervisor = Supervisor(bridge)

    supervisor_thread = threading.Thread(target=supervisor.run)
    supervisor_thread.setDaemon(True)
    supervisor_thread.start()

    if not args.no_control_ui:
        context.setContextProperty("naoqi_supervisor", supervisor)

        # Get the path of the current directory, and then add the name
        # of the QML file, to load it.
        qmlFile = join(dirname(__file__), 'main.qml')
        engine.load(abspath(qmlFile))

        if not engine.rootObjects():
            sys.exit(-1)

    if not args.no_tablet:
        tablet_webserver.ws_ip = bridge.tablet.WS_IP
        tablet_webserver.ws_port = bridge.tablet.WS_PORT

        bridge.setTabletUrl("http://%s:%s/" % (get_ip(), port))

        ## share the supervisor's cmd_queue with the tablet Flask server
        #tablet_webserver.cmd_queue = supervisor.cmd_queue

    # share the supervisor's cmd_queue with naoqi bridge
    bridge.cmd_queue = supervisor.cmd_queue

    ##################################################################



    if not args.no_control_ui:
        ok = app.exec_()
    else:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            ok = 0

    logger.info("Closing down...")
    bridge.tearDown()

    logger.info("Bye bye!")
    sys.exit(ok)
