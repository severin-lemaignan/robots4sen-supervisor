import logging

logger = logging.getLogger("robots.activities.listening")

import json
import time

from constants import *
from dialogues import get_dialogue
from events import Event

from activities.activity import Activity

class ListeningActivity(Activity):

    type = LISTENING

    def __init__(self):
        super(ListeningActivity, self).__init__()

    def start(self, robot, cmd_queue):
        super(ListeningActivity, self).start(robot, cmd_queue)

        # display the stop btn
        self.robot.tablet.clearAll()

        self.robot.say(get_dialogue("listening_prompt")).wait()

        btn = {"id": INTERRUPT, "img": "images/stop.svg"}
        self.robot.tablet.setCentered(btn)

    def run(self):

        while True:
            yield RUNNING

    def on_interrupted(self, evt):
        self.robot.say(get_dialogue("listening_end")).wait()
        return super(ListeningActivity, self).on_interrupted(evt)

    def on_no_one_engaged(self, evt):
        self.robot.say(get_dialogue("listening_no_one_left")).wait()
        return super(ListeningActivity, self).on_no_one_engaged(evt)

listening_activity = ListeningActivity()

def get_activity():
    return listening_activity

