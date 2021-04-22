import logging

logger = logging.getLogger("robots.activities.stories")

import time

from flask import render_template, redirect
from flask.helpers import url_for

from constants import *

from flask_server import tablet_webserver
from story_parser import Story

story = Story("static/stories/susanne-and-ben/story.json")

assets = "/static/stories/susanne-and-ben/assets/"

class Story:

    def __init__(self):

        self.tablet = None

        self.status = STOPPED
        self.progress = 0

    def __str__(self):
        return "Story telling"

    def start(self):
        # TODO: need to improve setUrl to ensure the page is fully loaded
        self.status = RUNNING
        time.sleep(1)
        self.tablet.setUrl("/activity/stories")
        time.sleep(1)

    def tick(self):

        #logger.info("Story progressing nicely. %s%% done" % self.progress)
        #self.progress+= 10

        return self.status

story_activity = Story()

def get_activity(tablet):
    story_activity.tablet = tablet
    return story_activity

@tablet_webserver.route('/activity/stories/<action>')
@tablet_webserver.route('/activity/stories/')
def web_stories(action=None):

    if action and action == REQUEST:
        # server.cmd_queue is injected by main.py upon Flask's thread creation
        tablet_webserver.cmd_queue.put((TABLET, STORIES, (action,)))
        return redirect(url_for('home_screen'))


    txt, actions, status = story.next(action)

    story_activity.status = status


    return render_template('stories.html',
                           text = txt,
                           path = assets,
                           actions = actions,
                           ws_server_ip = tablet_webserver.ws_ip,
                           ws_server_port = tablet_webserver.ws_port)



