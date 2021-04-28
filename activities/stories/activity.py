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

        self.story_txt = []
        self.step = 0

    def tick(self):

        #logger.info("Story progressing nicely. %s%% done" % self.progress)
        #self.progress+= 10
        
        if self.story_txt:
            
            if self.step == len(self.story_txt): # story finished!
                logger.info("STORY FINISHED")
                self.status = STOPPED
            else:
                sentence = self.story_txt[self.step]
                logger.info("STORY [%s/%s]: %s" % (self.step + 1, len(self.story_txt), sentence))
                self.robot.say(sentence).wait()
                self.step += 1

        return self.status

    def next(self, action):

        # if the robot is still speaking, wait until it is done
        if self.current_speech_action and \
           not self.current_speech_action.isFinished():
               logger.warning("Still speaking... waiting for the sentence to finish...")
               self.current_speech_action.wait()

        txt, actions = self.story.next(action)

        if len(actions) > 1:
            labels = [v["label"] for k, v in actions.items()]
            choice_sentence = ", ".join(labels[:-1]) + " or %s" % labels[-1]
            self.robot.glanceAtTablet()
            self.current_speech_action = self.robot.say("%s %s?" % (txt[0], choice_sentence))
            return txt[0], actions
        else:
            if len(txt) > 1: # it is a processed story, not just a confirmation

                # let's start the story itself!
                self.story_txt = txt

                # clear the tablet
                return None, None

            else:
                return self.next(actions.keys()[0]) # a Lunii confirmation -- we skip those


story_activity = StoryActivity()

def get_activity():
    return story_activity

@tablet_webserver.route('/activity/stories/<action>')
@tablet_webserver.route('/activity/stories/')
def web_stories(action=None):

    if action and action == REQUEST:
        # server.cmd_queue is injected by main.py upon Flask's thread creation
        tablet_webserver.cmd_queue.put((TABLET, STORIES, (action,)))
        return redirect(url_for('activities'))


    txt, actions = story_activity.next(action)

    if not txt:
        return redirect(url_for("waiting"))



    return render_template('stories.html',
                           text = txt,
                           path = assets,
                           actions = actions,
                           ws_server_ip = tablet_webserver.ws_ip,
                           ws_server_port = tablet_webserver.ws_port)



