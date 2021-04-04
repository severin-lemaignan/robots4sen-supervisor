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

    return render_template('index.html',
                           text = txt,
                           path = ASSETS,
                           actions = actions)


