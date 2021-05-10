import os
import json

from flask import Flask, url_for,render_template

import logging
logging.getLogger("werkzeug").setLevel(logging.WARNING)

from constants import *

tablet_webserver = Flask(__name__)

tablet_webserver.cmd_queue = None


@tablet_webserver.route('/')
def home_screen():

    return render_template('index.html',
                        options = {},
                        ws_server_ip = tablet_webserver.ws_ip,
                        ws_server_port = tablet_webserver.ws_port)

@tablet_webserver.route('/activities')
def activities():

    options = {"music": {"img":"images/music.svg", 
                         "label":"Music"}
              }
    return render_template('index.html',
                        options = options,
                        ws_server_ip = tablet_webserver.ws_ip,
                        ws_server_port = tablet_webserver.ws_port)

@tablet_webserver.route('/waiting')
def waiting():

    return render_template('index.html',
                        options = {},
                        ws_server_ip = tablet_webserver.ws_ip,
                        ws_server_port = tablet_webserver.ws_port)


