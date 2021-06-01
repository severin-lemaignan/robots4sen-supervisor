import logging

logger = logging.getLogger("robots.activities.cuddle")

import random

from constants import *
from dialogues import get_dialogue
from events import Event

from activities.activity import Activity

class CuddleActivity(Activity):

    type = CUDDLE

    def __init__(self):
        super(CuddleActivity, self).__init__()

        self.stop_behaviour = False

    def run(self):

        self.robot.tablet.clearOptions()
        self.robot.say(get_dialogue("cuddle_start")).wait()
        yield RUNNING

        behaviours = ["robots4sen-brl/cuddle"]

        behaviour = self.robot.run_behaviour(random.choice(behaviours))

        while behaviour.isRunning():
            if self.stop_behaviour:
                behaviour.cancel()
                self.stop_behaviour = False
            yield RUNNING

    def terminate(self):
        self.stop_behaviour = True
        next(self._behaviour) # run it one more time to ensure the naoqi behaviour is cancelled
        return STOPPED


activity = CuddleActivity()

def get_activity():
    return activity
