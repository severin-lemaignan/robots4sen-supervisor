import logging

logger = logging.getLogger("robots.activities.stories")

import json
import time

from flask import render_template, redirect
from flask.helpers import url_for

from constants import *
from dialogues import get_dialogue
from events import Event

from flask_server import tablet_webserver
from story_parser import Story
from activities.activity import Activity

assets_path = "stories/susanne-and-ben/assets/"

class StoryActivity(Activity):

    type = STORY

    def __init__(self):
        super(StoryActivity, self).__init__()

        self.story = Story("static/stories/susanne-and-ben/story.json")

    def run(self):
 
        self.robot.tablet.clearAll()
        self.robot.say(get_dialogue("story_prompt")).wait()
        yield RUNNING

        self.robot.tablet.addCancelBtn()
        
        ####################################################################
        ### START THE STORY-BUILDING TREE

        txt, actions = self.story.next()

        while len(actions) > 1 \
              or len(txt) == 1: # Lunii confirmation step -- skip it

            if len(actions) == 1: # Lunii confirmation step -- skip it

                txt, actions = self.story.next(actions.keys()[0])
                continue


            labels = [v["label"] for k, v in actions.items()]
            choice_sentence = ", ".join(labels[:-1]) + " or %s" % labels[-1]
            options = [{"id":k, "label": v["label"], "img": assets_path + v["img"]} for k, v in actions.items()]
            options_text = "".join(["\\option=%s\\" % json.dumps(o) for o in options])
            self.robot.glanceAtTablet()
            self.robot.tablet.clearOptions()
            self.robot.say("%s\\pau=500\\" % txt[0]).wait()
            yield RUNNING
            self.robot.say("%s %s?" % (options_text, choice_sentence))
            yield RUNNING
            
            while self.response_queue.empty():
                yield RUNNING
            next_action = self.response_queue.get()["id"]


            txt, actions = self.story.next(next_action)

        ####################################################################
        ### STARTS THE STORY ITSELF

        assert(len(txt) > 1) # it is a processed story, not just a confirmation

        time.sleep(1)
        yield RUNNING
        self.robot.say(get_dialogue("story_start")).wait()
        yield RUNNING
        time.sleep(1)
        yield RUNNING

        self.robot.tablet.clearAll()
        btn = {"id": INTERRUPT, "img": "images/stop.svg"}
        self.robot.tablet.setCentered(btn)

        for idx, sentence in enumerate(txt):
            logger.info("STORY [%s/%s]: %s" % (idx + 1, len(txt), sentence))
            self.robot.say(sentence).wait()
            yield RUNNING

        logger.info("STORY FINISHED")
        time.sleep(1)
        yield RUNNING
        self.robot.say(get_dialogue("story_end")).wait()
        yield RUNNING
        time.sleep(1)

    def on_interrupted(self, evt):
        self.robot.say(get_dialogue("story_interrupted")).wait()
        return super(StoryActivity, self).on_interrupted(evt)

    def on_no_one_engaged(self, evt):
        self.robot.say(get_dialogue("story_no_one_left")).wait()
        return super(StoryActivity, self).on_no_one_engaged(evt)

story_activity = StoryActivity()

def get_activity():
    return story_activity

