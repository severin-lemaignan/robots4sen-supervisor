import logging

logger = logging.getLogger("robots.activities.stories")

import json
import time

from flask import render_template, redirect
from flask.helpers import url_for

from constants import *
from dialogues import get_dialogue

from flask_server import tablet_webserver
from story_parser import Story


assets_path = "stories/susanne-and-ben/assets/"

class StoryActivity:

    def __init__(self):

        self.story = Story("static/stories/susanne-and-ben/story.json")

        self.status = STOPPED
        self.progress = 0

        self.current_speech_action = None


    def __str__(self):
        return "Story telling"

    def start(self, robot):

        self.robot = robot

        # TODO: need to improve setUrl to ensure the page is fully loaded
        self.status = RUNNING
        self.robot.tablet.clearOptions()
        self.robot.say(get_dialogue("story_prompt")).wait()
        time.sleep(1)
        self.robot.tablet.debug("activity/stories")
        #self.tablet.setUrl("/activity/stories")
        #time.sleep(1)

        self.story_txt = []
        self.step = 0

        # this start the story building tree
        self.next(None)

    def tick(self):

        #logger.info("Story progressing nicely. %s%% done" % self.progress)
        #self.progress+= 10
        
        if self.story_txt:
            
            if self.step == len(self.story_txt): # story finished!
                logger.info("STORY FINISHED")
                self.status = STOPPED
                time.sleep(1)
                self.robot.say(get_dialogue("story_end")).wait()
                time.sleep(1)
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
            options = [{"id":k, "label": v["label"], "img": assets_path + v["img"]} for k, v in actions.items()]
            options_text = "".join(["\\option=%s\\" % json.dumps(o) for o in options])
            self.robot.glanceAtTablet()
            self.current_speech_action = self.robot.say("%s\\pau=500\\" % txt[0]).wait()
            self.current_speech_action = self.robot.say("%s %s?" % (options_text, choice_sentence))
            
            # blocking call: we wait until the user chose what option he/she wants
            next_action = self.robot.tablet.response_queue.get()

            return self.next(next_action)

        else:
            if len(txt) > 1: # it is a processed story, not just a confirmation

                time.sleep(1)
                self.robot.say(get_dialogue("story_start")).wait()
                time.sleep(1)

                # let's start the story itself!
                self.story_txt = txt

                # clear the tablet
                return None, None

            else:
                return self.next(actions.keys()[0]) # a Lunii confirmation -- we skip those


story_activity = StoryActivity()

def get_activity():
    return story_activity

