import logging;logger = logging.getLogger("robots.activities.stories")

import time

from flask import render_template

from constants import *

from flask_server import tablet_webserver
from story_parser import Story

story = Story("static/stories/susanne-and-ben/story.json")

assets = "/static/stories/susanne-and-ben/assets/"

def start_activity(robot, tablet, progress):

    tablet.setUrl("/stories")

    progress = 0

    for i in range(10):
        time.sleep(1)
        logger.info("Story progressing nicely. %s%% done" % progress)
        progress+= 10

    

@tablet_webserver.route('/stories/<action>')
@tablet_webserver.route('/stories/')
def web_stories(action=None):

    txt, actions = story.next(action)

    # server.cmd_queue is injected by main.py upon Flask's thread creation
    tablet_webserver.cmd_queue.put((TABLET, STORIES, (action,)))

    return render_template('stories.html',
                           text = txt,
                           path = assets,
                           actions = actions)


