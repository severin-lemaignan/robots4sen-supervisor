import logging

logger = logging.getLogger("robots.activities.stories")

import time

from flask import render_template, redirect
from flask.helpers import url_for

from constants import *
from dialogues import get_dialogue

from flask_server import tablet_webserver
from story_parser import Story


assets = "/static/stories/susanne-and-ben/assets/"

class StoryActivity:

    def __init__(self):

        self.story = Story("static/stories/susanne-and-ben/story.json")

        self.tablet = None

        self.status = STOPPED
        self.progress = 0

        self.current_speech_action = None


    def __str__(self):
        return "Story telling"

    def start(self, tablet, robot):

        self.tablet = tablet
        self.robot = robot

        # TODO: need to improve setUrl to ensure the page is fully loaded
        self.status = RUNNING
        self.robot.say(get_dialogue("story_prompt")).wait()
        time.sleep(1)
        self.tablet.setUrl("/activity/stories")
        time.sleep(1)

    def tick(self):

        #logger.info("Story progressing nicely. %s%% done" % self.progress)
        #self.progress+= 10

        return self.status

    def next(self, action):

        # if the robot is still speaking, wait until it is done
        if self.current_speech_action and \
           not self.current_speech_action.isFinished():
               self.current_speech_action.wait()

        txt, actions = self.story.next(action)

        if len(actions) > 1:
            labels = [v["label"] for k, v in actions.items()]
            choice_sentence = ", ".join(labels[:-1]) + " or %s" % labels[-1]
            self.current_speech_action = self.robot.say("%s %s?" % (txt, choice_sentence))
        else:
            if len(txt) > 300: # it is the story, not just a confirmation
                chuncks = txt.split(".")
                for idx, c in enumerate(chuncks):
                    logger.info("STORY [%s/%s]: %s" % (idx + 1, len(chuncks), c))
                    self.robot.say(c).wait()

            else:
                return self.next(actions.keys()[0])

        return txt, actions

story_activity = StoryActivity()

def get_activity():
    return story_activity

@tablet_webserver.route('/activity/stories/<action>')
@tablet_webserver.route('/activity/stories/')
def web_stories(action=None):

    if action and action == REQUEST:
        # server.cmd_queue is injected by main.py upon Flask's thread creation
        tablet_webserver.cmd_queue.put((TABLET, STORIES, (action,)))
        return redirect(url_for('home_screen'))


    txt, actions = story_activity.next(action)



    return render_template('stories.html',
                           text = txt,
                           path = assets,
                           actions = actions,
                           ws_server_ip = tablet_webserver.ws_ip,
                           ws_server_port = tablet_webserver.ws_port)



