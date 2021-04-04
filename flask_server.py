import os
import json

from flask import Flask, escape, url_for,render_template, g, request, redirect, jsonify, session


from story_parser import Story

server = Flask(__name__)


ASSETS = "static/stories/susanne-and-ben/assets/"

story = Story("static/stories/susanne-and-ben/story.json")

@server.route('/<action>')
@server.route('/')
def main(action=None):

    txt, actions = story.next(action)

    # server.cmd_queue is injected by main.py upon Flask's thread creation
    server.cmd_queue.put("Hello")

    return render_template('index.html',
                           text = txt,
                           path = ASSETS,
                           actions = actions)


