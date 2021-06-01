import logging
logger = logging.getLogger("robots.activities.calm_music")

import random

from constants import *
from dialogues import get_dialogue
from events import Event

from activities.activity import Activity

class CalmMusicActivity(Activity):

    type = CALM_MUSIC

    def __init__(self):
        super(CalmMusicActivity, self).__init__()
        self.stop_behaviour = False

    def run(self):

        self.robot.tablet.clearOptions()
        self.robot.say(get_dialogue("calm_music_start")).wait()
        yield RUNNING

        behaviours = ["robots4sen-brl/calm_music"]

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

activity = CalmMusicActivity()

def get_activity():
    return activity
