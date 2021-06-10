import logging

logger = logging.getLogger("robots.activities.relax_sounds")

import random

from constants import *
from dialogues import get_dialogue
from events import Event
from activities.activity import Activity

class RelaxSoundsActivity(Activity):

    type = RELAX_SOUNDS

    def __init__(self):
        super(RelaxSoundsActivity, self).__init__()

        self.stop_behaviour = False

    def run(self):

        self.robot.tablet.clearAll()
        self.robot.say(get_dialogue("relax_sounds_start")).wait()

        btn = {"id": INTERRUPT, "img": "images/stop.svg"}
        self.robot.tablet.setCentered(btn)

        yield RUNNING

        behaviours = ["robots4sen-brl/relax_sounds"]

        behaviour = self.robot.run_behaviour(random.choice(behaviours))

        while behaviour.isRunning():
            if self.stop_behaviour:
                behaviour.cancel()
                self.stop_behaviour = False
            yield RUNNING

    def terminate(self):
        self.stop_behaviour = True
        next(self._behaviour) # run it one more time to ensure the naoqi behaviour is cancelled
        return INTERRUPTED

activity = RelaxSoundsActivity()

def get_activity():
    return activity
