import os
import json

from flask import Flask, escape, url_for,render_template, g, request, redirect, jsonify, session


from story_parser import Story

server = Flask(__name__)

NAME = "TABLET"

ASSETS = "/static/stories/susanne-and-ben/assets/"

story = Story("static/stories/susanne-and-ben/story.json")

@server.route('/')
def main():

    # server.cmd_queue is injected by main.py upon Flask's thread creation
    server.cmd_queue.put((NAME, "INDEX", None))

    return render_template('index.html')


@server.route('/stories/<action>')
@server.route('/stories/')
def stories(action=None):

    txt, actions = story.next(action)

    # server.cmd_queue is injected by main.py upon Flask's thread creation
    server.cmd_queue.put((NAME, "STORIES", None))

    return render_template('stories.html',
                           text = txt,
                           path = ASSETS,
                           actions = actions)


