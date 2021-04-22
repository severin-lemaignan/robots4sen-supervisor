import os
import json

from flask import Flask, url_for,render_template

from constants import *

tablet_webserver = Flask(__name__)

tablet_webserver.cmd_queue = None


@tablet_webserver.route('/')
def home_screen():

    if tablet_webserver.cmd_queue:
        # server.cmd_queue is injected by main.py upon Flask's thread creation
        tablet_webserver.cmd_queue.put((TABLET, NONE, None))

    return render_template('index.html',
                        ws_server_ip = tablet_webserver.ws_ip,
                        ws_server_port = tablet_webserver.ws_port)


