import os
import json

from flask import Flask, escape, url_for,render_template, g, request, redirect, jsonify, session
from werkzeug import secure_filename

from pathlib import Path

from story_parser import Story

app = Flask(__name__)

ROOT = Path(os.path.dirname(__file__))

ASSETS = "static/stories/susanne-and-ben/assets/"

story = Story("static/stories/susanne-and-ben/story.json")

@app.route('/<action>')
@app.route('/')
def main(action=None):

    txt, actions = story.next(action)

    return render_template('index.html',
                           text = txt,
                           path = ASSETS,
                           actions = actions)


