import logging
logger = logging.getLogger("robots.activities.calm_dances")

import random

from constants import *
from dialogues import get_dialogue
from events import Event

from activities.activity import Activity

class CalmDancesActivity(Activity):

    type = CALM_DANCES

    def __init__(self):
        super(CalmDancesActivity, self).__init__()

    def start(self, robot, cmd_queue):

        self.robot = robot
        self.cmd_queue = cmd_queue
        self.response_queue = self.robot.tablet.response_queue

        self.robot.tablet.debug("activity/calm_dances")

        self.stop_behaviour = False

    def run(self):

        self.robot.tablet.clearOptions()
        self.robot.say(get_dialogue("calm_dances_start")).wait()
        yield RUNNING

        behaviours = ["robots4sen-brl/dance-taichi"]

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

activity = CalmDancesActivity()

def get_activity():
    return activity
