import os
import json

from flask import Flask, url_for,render_template

from constants import *

tablet_webserver = Flask(__name__)




@tablet_webserver.route('/')
def main():

    # server.cmd_queue is injected by main.py upon Flask's thread creation
    tablet_webserver.cmd_queue.put((TABLET, NONE, None))

    return render_template('index.html')


