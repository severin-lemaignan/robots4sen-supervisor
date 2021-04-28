import os
import json

from flask import Flask, url_for,render_template

from constants import *

tablet_webserver = Flask(__name__)

tablet_webserver.cmd_queue = None


@tablet_webserver.route('/')
def home_screen():

    return render_template('index.html',
                        ws_server_ip = tablet_webserver.ws_ip,
                        ws_server_port = tablet_webserver.ws_port)

@tablet_webserver.route('/activities')
def activities():

    return render_template('activities.html',
                        ws_server_ip = tablet_webserver.ws_ip,
                        ws_server_port = tablet_webserver.ws_port)

@tablet_webserver.route('/waiting')
def waiting():

    return render_template('waiting.html',
                        ws_server_ip = tablet_webserver.ws_ip,
                        ws_server_port = tablet_webserver.ws_port)


